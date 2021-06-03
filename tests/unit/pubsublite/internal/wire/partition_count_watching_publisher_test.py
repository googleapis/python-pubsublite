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

from google.cloud.pubsublite.internal.wire.partition_count_watcher import (
    PartitionCountWatcher,
)
from google.cloud.pubsublite.internal.wire.partition_count_watching_publisher import (
    PartitionCountWatchingPublisher,
)
from google.cloud.pubsublite.internal.wire.publisher import Publisher
from google.cloud.pubsublite.internal.wire.routing_policy import RoutingPolicy
from google.cloud.pubsublite.testing.test_utils import wire_queues, run_on_thread
from google.cloud.pubsublite.types import Partition
from google.cloud.pubsublite_v1 import PubSubMessage
from google.api_core.exceptions import GoogleAPICallError

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def mock_publishers():
    return {Partition(i): MagicMock(spec=Publisher) for i in range(10)}


@pytest.fixture()
def mock_policies():
    return {i: MagicMock(spec=RoutingPolicy) for i in range(10)}


@pytest.fixture()
def mock_watcher():
    watcher = MagicMock(spec=PartitionCountWatcher)
    return watcher


@pytest.fixture()
def publisher(mock_watcher, mock_publishers, mock_policies):
    return run_on_thread(
        lambda: PartitionCountWatchingPublisher(
            mock_watcher, lambda p: mock_publishers[p], lambda c: mock_policies[c]
        )
    )


async def test_init(mock_watcher, publisher):
    mock_watcher.get_partition_count.return_value = 2
    async with publisher:
        mock_watcher.__aenter__.assert_called_once()
        pass
    mock_watcher.__aexit__.assert_called_once()


async def test_failed_init(mock_watcher, publisher):
    mock_watcher.get_partition_count.side_effect = GoogleAPICallError("error")
    with pytest.raises(GoogleAPICallError):
        await publisher.__aenter__()
    mock_watcher.__aenter__.assert_called_once()
    mock_watcher.__aexit__.assert_called_once()
    await publisher.__aexit__(None, None, None)


async def test_simple_publish(mock_publishers, mock_policies, mock_watcher, publisher):
    mock_watcher.get_partition_count.return_value = 2
    async with publisher:
        mock_policies[2].route.return_value = Partition(1)
        mock_publishers[Partition(1)].publish.return_value = "a"
        await publisher.publish(PubSubMessage())
        mock_policies[2].route.assert_called_with(PubSubMessage())
        mock_publishers[Partition(1)].publish.assert_called()


async def test_publish_after_increase(
    mock_publishers, mock_policies, mock_watcher, publisher
):
    get_queues = wire_queues(mock_watcher.get_partition_count)
    await get_queues.results.put(2)
    async with publisher:
        get_queues.called.get_nowait()

        mock_policies[2].route.return_value = Partition(1)
        mock_publishers[Partition(1)].publish.return_value = "a"
        await publisher.publish(PubSubMessage())
        mock_policies[2].route.assert_called_with(PubSubMessage())
        mock_publishers[Partition(1)].publish.assert_called()

        await get_queues.called.get()
        await get_queues.results.put(3)
        await get_queues.called.get()

        mock_policies[3].route.return_value = Partition(2)
        mock_publishers[Partition(2)].publish.return_value = "a"
        await publisher.publish(PubSubMessage())
        mock_policies[3].route.assert_called_with(PubSubMessage())
        mock_publishers[Partition(2)].publish.assert_called()


async def test_decrease_ignored(
    mock_publishers, mock_policies, mock_watcher, publisher
):
    get_queues = wire_queues(mock_watcher.get_partition_count)
    await get_queues.results.put(2)
    async with publisher:
        get_queues.called.get_nowait()

        mock_policies[2].route.return_value = Partition(1)
        mock_publishers[Partition(1)].publish.return_value = "a"
        await publisher.publish(PubSubMessage())
        mock_policies[2].route.assert_called_with(PubSubMessage())
        mock_publishers[Partition(1)].publish.assert_called()

        await get_queues.called.get()
        await get_queues.results.put(1)
        await get_queues.called.get()

        mock_policies[2].route.return_value = Partition(1)
        mock_publishers[Partition(1)].publish.return_value = "a"
        await publisher.publish(PubSubMessage())
        mock_policies[2].route.assert_called_with(PubSubMessage())
        mock_publishers[Partition(1)].publish.assert_called()
