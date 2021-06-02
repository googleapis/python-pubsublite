# Copyright 2020 Google LLC
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

from asynctest.mock import MagicMock
import pytest

from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_publisher_client import (
    MultiplexedPublisherClient,
)
from google.cloud.pubsublite.cloudpubsub.internal.single_publisher import (
    SinglePublisher,
)
from google.cloud.pubsublite.types import TopicPath
from google.api_core.exceptions import GoogleAPICallError


@pytest.fixture()
def topic1():
    return TopicPath.parse("projects/1/locations/us-central1-a/topics/topic1")


@pytest.fixture()
def topic2():
    return TopicPath.parse("projects/1/locations/us-central1-a/topics/topic2")


@pytest.fixture()
def topic1_publisher():
    topic1_publisher = MagicMock(spec=SinglePublisher)
    return topic1_publisher


@pytest.fixture()
def topic2_publisher():
    topic2_publisher = MagicMock(spec=SinglePublisher)
    return topic2_publisher


@pytest.fixture()
def multiplexed_publisher(topic1, topic1_publisher, topic2_publisher):
    return MultiplexedPublisherClient(
        lambda topic: topic1_publisher if topic == topic1 else topic2_publisher
    )


def test_multiplexed_publish(
    topic1, topic2, topic1_publisher, topic2_publisher, multiplexed_publisher
):
    topic1_publisher.__enter__.return_value = topic1_publisher
    topic2_publisher.__enter__.return_value = topic2_publisher
    with multiplexed_publisher:
        multiplexed_publisher.publish(topic1, data=b"abc")
        topic1_publisher.__enter__.assert_called_once()
        topic1_publisher.publish.assert_called_once_with(data=b"abc", ordering_key="")
        multiplexed_publisher.publish(topic2, data=b"abc")
        topic2_publisher.__enter__.assert_called_once()
        topic2_publisher.publish.assert_called_once_with(data=b"abc", ordering_key="")
    topic1_publisher.__exit__.assert_called_once()
    topic2_publisher.__exit__.assert_called_once()


def test_publisher_init_failure(topic1, topic1_publisher, multiplexed_publisher):
    topic1_publisher.__enter__.side_effect = GoogleAPICallError("error")
    with multiplexed_publisher:
        future = multiplexed_publisher.publish(topic1, data=b"abc")
    with pytest.raises(GoogleAPICallError):
        future.result()
