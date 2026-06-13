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

import asyncio
from unittest.mock import MagicMock, patch

from google.api_core.exceptions import InternalServerError
from google.cloud.pubsublite.cloudpubsub.internal.kafka_publisher import (
    KafkaPublisherClient,
    AsyncKafkaPublisherClient,
)
import pytest

mock_confluent_kafka = None


@pytest.fixture(autouse=True)
def setup_local_mock(confluent_kafka_mock):
    global mock_confluent_kafka
    mock_confluent_kafka = confluent_kafka_mock


def test_sync_kafka_publisher_client_lifecycle():
    bootstrap_servers = "localhost:9092"
    kafka_properties = {"client.id": "test-client"}

    with KafkaPublisherClient(bootstrap_servers, kafka_properties) as client:
        mock_confluent_kafka.Producer.assert_called_once()
        config = mock_confluent_kafka.Producer.call_args[0][0]
        assert config["bootstrap.servers"] == bootstrap_servers
        assert config["client.id"] == "test-client"
        assert config["security.protocol"] == "SASL_SSL"
        assert config["sasl.mechanisms"] == "OAUTHBEARER"
        assert config["oauth_cb"] is not None
        assert config["enable.idempotence"] is True

        assert client._poll_thread.is_alive()

    # After exiting block, it should shutdown
    assert not client._running
    client._producer.flush.assert_called_once()


def test_sync_kafka_publish_success():
    bootstrap_servers = "localhost:9092"
    producer_mock = MagicMock()
    mock_confluent_kafka.Producer.return_value = producer_mock

    # Capture callback
    callback_capture = []

    def mock_produce(topic, value, key, headers, callback):
        callback_capture.append(callback)

    producer_mock.produce.side_effect = mock_produce

    with KafkaPublisherClient(bootstrap_servers) as client:
        future = client.publish(
            topic="projects/p/locations/l/topics/t",
            data=b"payload",
            ordering_key="key",
            attr1="val1",
        )

        producer_mock.produce.assert_called_once()
        call_kwargs = producer_mock.produce.call_args[1]
        assert call_kwargs["topic"] == "projects/p/locations/l/topics/t"
        assert call_kwargs["value"] == b"payload"
        assert call_kwargs["key"] == b"key"
        assert ("attr1", b"val1") in call_kwargs["headers"]

        # Trigger callback with success
        mock_msg = MagicMock()
        mock_msg.partition.return_value = 2
        mock_msg.offset.return_value = 100
        callback_capture[0](None, mock_msg)

        assert future.done()
        assert future.result() == "2:100"


def test_sync_kafka_publish_failure():
    bootstrap_servers = "localhost:9092"
    producer_mock = MagicMock()
    mock_confluent_kafka.Producer.return_value = producer_mock

    callback_capture = []

    def mock_produce(topic, value, key, headers, callback):
        callback_capture.append(callback)

    producer_mock.produce.side_effect = mock_produce

    with KafkaPublisherClient(bootstrap_servers) as client:
        future = client.publish(
            topic="projects/p/locations/l/topics/t", data=b"payload"
        )

        # Trigger callback with error
        callback_capture[0]("some_kafka_error", None)

        assert future.done()
        with pytest.raises(InternalServerError):
            future.result()


@patch(
    "google.cloud.pubsublite.cloudpubsub.message_transforms._decode_attribute_event_time_proto"
)
def test_sync_kafka_publish_with_event_time(mock_decode):
    mock_ts = MagicMock()
    mock_ts.seconds = 12345
    mock_ts.nanos = 67890
    mock_decode.return_value = mock_ts

    bootstrap_servers = "localhost:9092"
    producer_mock = MagicMock()
    mock_confluent_kafka.Producer.return_value = producer_mock

    with KafkaPublisherClient(bootstrap_servers) as client:
        client.publish(
            topic="projects/p/locations/l/topics/t",
            data=b"payload",
            **{"x-goog-pubsublite-event-time": "serialized_proto"},
        )

        call_kwargs = producer_mock.produce.call_args[1]
        headers = call_kwargs["headers"]
        assert ("pubsublite.event_time", b"12345.000067890") in headers
        mock_decode.assert_called_once_with("serialized_proto")


@pytest.mark.asyncio
async def test_async_kafka_publisher_client_lifecycle():
    bootstrap_servers = "localhost:9092"
    client = AsyncKafkaPublisherClient(bootstrap_servers)
    mock_confluent_kafka.Producer.assert_called_once()
    assert client._poll_thread.is_alive()

    async with client:
        pass

    assert not client._running
    client._producer.flush.assert_called_once()


@pytest.mark.asyncio
async def test_async_kafka_publish_success():
    bootstrap_servers = "localhost:9092"
    producer_mock = MagicMock()
    mock_confluent_kafka.Producer.return_value = producer_mock

    callback_capture = []

    def mock_produce(topic, value, key, headers, callback):
        callback_capture.append(callback)

    producer_mock.produce.side_effect = mock_produce

    client = AsyncKafkaPublisherClient(bootstrap_servers)
    async with client:
        publish_task = asyncio.create_task(
            client.publish(
                topic="projects/p/locations/l/topics/t",
                data=b"payload",
                ordering_key="key",
            )
        )

        # Yield to let the publish call run and schedule
        await asyncio.sleep(0.01)

        producer_mock.produce.assert_called_once()

        # Trigger callback with success (simulating background thread)
        mock_msg = MagicMock()
        mock_msg.partition.return_value = 3
        mock_msg.offset.return_value = 200
        callback_capture[0](None, mock_msg)

        result = await publish_task
        assert result == "3:200"


@pytest.mark.asyncio
async def test_async_kafka_publish_failure():
    bootstrap_servers = "localhost:9092"
    producer_mock = MagicMock()
    mock_confluent_kafka.Producer.return_value = producer_mock

    callback_capture = []

    def mock_produce(topic, value, key, headers, callback):
        callback_capture.append(callback)

    producer_mock.produce.side_effect = mock_produce

    client = AsyncKafkaPublisherClient(bootstrap_servers)
    async with client:
        publish_task = asyncio.create_task(
            client.publish(topic="projects/p/locations/l/topics/t", data=b"payload")
        )

        await asyncio.sleep(0.01)

        callback_capture[0]("some_kafka_error", None)

        with pytest.raises(InternalServerError):
            await publish_task
