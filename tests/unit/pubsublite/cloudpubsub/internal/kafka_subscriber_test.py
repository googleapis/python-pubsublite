# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from unittest.mock import MagicMock, call
import pytest
import asyncio
from datetime import datetime, timezone

mock_confluent_kafka = None

from google.cloud.pubsublite.cloudpubsub.internal.kafka_subscriber import (
    KafkaAsyncSingleSubscriber,
)
from google.cloud.pubsublite.types import SubscriptionPath, Partition

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def setup_local_mock(confluent_kafka_mock):
    global mock_confluent_kafka
    mock_confluent_kafka = confluent_kafka_mock


@pytest.fixture()
def consumer_mock():
    mock = MagicMock()
    mock.poll.return_value = None
    mock_confluent_kafka.Consumer.return_value = mock
    return mock


class MockMessage:

    def __init__(
        self,
        value=b"val",
        key=b"key",
        partition=0,
        offset=0,
        headers=None,
        timestamp=(1, 1000),
        err=None,
    ):
        self._value = value
        self._key = key
        self._partition = partition
        self._offset = offset
        self._headers = headers or []
        self._timestamp = timestamp
        self._err = err

    def value(self):
        return self._value

    def key(self):
        return self._key

    def partition(self):
        return self._partition

    def offset(self):
        return self._offset

    def headers(self):
        return self._headers

    def timestamp(self):
        return self._timestamp

    def error(self):
        return self._err

    def topic(self):
        return "test-topic"


async def test_kafka_subscriber_lifecycle_subscribe(consumer_mock):
    sub_path = SubscriptionPath.parse(
        "projects/p/locations/us-central1-a/subscriptions/s"
    )
    bootstrap_servers = "localhost:9092"
    kafka_topic = "test-topic"

    subscriber = KafkaAsyncSingleSubscriber(
        subscription=sub_path,
        fixed_partitions=None,
        bootstrap_servers=bootstrap_servers,
        kafka_topic=kafka_topic,
    )

    async with subscriber:
        mock_confluent_kafka.Consumer.assert_called_once()
        config = mock_confluent_kafka.Consumer.call_args[0][0]
        assert config["bootstrap.servers"] == bootstrap_servers
        # Derived group ID: slashes replaced by dashes
        assert (
            config["group.id"]
            == "projects-p-locations-us-central1-a-subscriptions-s"
        )
        assert config["enable.auto.commit"] is False

        # Verify subscribe was called on consumer
        consumer_mock.subscribe.assert_called_once_with([kafka_topic])
        assert subscriber._poll_thread.is_alive()

    # After exit, consumer should be closed
    consumer_mock.close.assert_called_once()
    assert not subscriber._running


async def test_kafka_subscriber_lifecycle_assign(consumer_mock):
    sub_path = SubscriptionPath.parse(
        "projects/p/locations/us-central1-a/subscriptions/s"
    )
    bootstrap_servers = "localhost:9092"
    kafka_topic = "test-topic"
    fixed_partitions = {Partition(1), Partition(3)}

    # Mock TopicPartition construction
    tp_mock = MagicMock()
    mock_confluent_kafka.TopicPartition = tp_mock

    subscriber = KafkaAsyncSingleSubscriber(
        subscription=sub_path,
        fixed_partitions=fixed_partitions,
        bootstrap_servers=bootstrap_servers,
        kafka_topic=kafka_topic,
    )

    async with subscriber:
        # Verify assign was called
        # Order of partitions in set can vary, so check calls
        tp_mock.assert_has_calls(
            [call(kafka_topic, 1), call(kafka_topic, 3)], any_order=True
        )
        assert consumer_mock.assign.called
        consumer_mock.subscribe.assert_not_called()


async def test_kafka_subscriber_read_success(consumer_mock):
    sub_path = SubscriptionPath.parse(
        "projects/p/locations/us-central1-a/subscriptions/s"
    )

    # Return one message and then None
    msg = MockMessage(value=b"payload", key=b"my-key", partition=1, offset=50)
    poll_results = [msg]

    def mock_poll(timeout):
        return poll_results.pop(0) if poll_results else None

    consumer_mock.poll.side_effect = mock_poll

    subscriber = KafkaAsyncSingleSubscriber(
        subscription=sub_path,
        fixed_partitions=None,
        bootstrap_servers="localhost",
        kafka_topic="topic",
    )

    async with subscriber:
        # Wait a bit for poll thread to run and put message in queue
        await asyncio.sleep(0.1)

        batch = await subscriber.read()
        assert len(batch) == 1
        wrapped_msg = batch[0]

        assert wrapped_msg.data == b"payload"
        assert wrapped_msg.ordering_key == "my-key"
        assert wrapped_msg.message_id == "test-topic:1:50"
        # Publish time: 1000ms -> 1s
        assert wrapped_msg.publish_time == datetime(
            1970, 1, 1, 0, 0, 1, tzinfo=timezone.utc
        )

        # Metadata attributes
        assert wrapped_msg.attributes["x-kafka-topic"] == "test-topic"
        assert wrapped_msg.attributes["x-kafka-partition"] == "1"
        assert wrapped_msg.attributes["x-kafka-offset"] == "50"


async def test_kafka_subscriber_read_with_event_time(consumer_mock):
    sub_path = SubscriptionPath.parse(
        "projects/p/locations/us-central1-a/subscriptions/s"
    )

    # Message with pubsublite.event_time header
    headers = [("pubsublite.event_time", b"12345.000067890")]
    msg = MockMessage(value=b"val", headers=headers)
    poll_results = [msg]

    def mock_poll(timeout):
        return poll_results.pop(0) if poll_results else None

    consumer_mock.poll.side_effect = mock_poll

    subscriber = KafkaAsyncSingleSubscriber(
        subscription=sub_path,
        fixed_partitions=None,
        bootstrap_servers="localhost",
        kafka_topic="topic",
    )

    async with subscriber:
        await asyncio.sleep(0.1)
        batch = await subscriber.read()
        wrapped_msg = batch[0]

        # Verify event time attribute is set and encoded correctly
        assert "x-goog-pubsublite-event-time" in wrapped_msg.attributes
        from google.cloud.pubsublite.cloudpubsub.message_transforms import (
            decode_attribute_event_time,
        )

        dt = decode_attribute_event_time(
            wrapped_msg.attributes["x-goog-pubsublite-event-time"]
        )
        assert dt.timestamp() == 12345.000067


async def test_kafka_subscriber_read_with_duplicate_headers(consumer_mock):
    sub_path = SubscriptionPath.parse(
        "projects/p/locations/us-central1-a/subscriptions/s"
    )

    # Duplicate headers
    headers = [("h1", b"v1"), ("h1", b"v2"), ("h2", b"v3")]
    msg = MockMessage(value=b"val", headers=headers)
    poll_results = [msg]

    def mock_poll(timeout):
        return poll_results.pop(0) if poll_results else None

    consumer_mock.poll.side_effect = mock_poll

    subscriber = KafkaAsyncSingleSubscriber(
        subscription=sub_path,
        fixed_partitions=None,
        bootstrap_servers="localhost",
        kafka_topic="topic",
    )

    async with subscriber:
        await asyncio.sleep(0.1)
        batch = await subscriber.read()
        wrapped_msg = batch[0]

        # Flat map with suffixes for duplicates
        assert wrapped_msg.attributes["h1"] == "v1"
        assert wrapped_msg.attributes["h1.1"] == "v2"
        assert wrapped_msg.attributes["h2"] == "v3"


async def test_kafka_subscriber_ack_commit(consumer_mock):
    sub_path = SubscriptionPath.parse(
        "projects/p/locations/us-central1-a/subscriptions/s"
    )

    msg = MockMessage(partition=2, offset=99)
    poll_results = [msg]

    def mock_poll(timeout):
        return poll_results.pop(0) if poll_results else None

    consumer_mock.poll.side_effect = mock_poll

    subscriber = KafkaAsyncSingleSubscriber(
        subscription=sub_path,
        fixed_partitions=None,
        bootstrap_servers="localhost",
        kafka_topic="topic",
    )

    # Mock TopicPartition for commit verification
    tp_mock = MagicMock()
    mock_confluent_kafka.TopicPartition = tp_mock

    async with subscriber:
        await asyncio.sleep(0.1)
        batch = await subscriber.read()
        wrapped_msg = batch[0]

        # Ack the message
        wrapped_msg.ack()

        # Wait for commit queue to be processed in poll loop
        await asyncio.sleep(0.2)

        # Verify commit was called with offset + 1
        tp_mock.assert_called_with("topic", 2, 100)
        consumer_mock.commit.assert_called_once()
        call_kwargs = consumer_mock.commit.call_args[1]
        assert call_kwargs["asynchronous"] is True
