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
import asyncio
import queue
from asynctest.mock import MagicMock
import pytest

from google.cloud.pubsublite import AdminClientInterface
from google.cloud.pubsublite.internal.wire.partition_count_watcher_impl import (
    PartitionCountWatcherImpl,
)
from google.cloud.pubsublite.internal.wire.publisher import Publisher
from google.cloud.pubsublite.testing.test_utils import run_on_thread
from google.cloud.pubsublite.types import Partition, TopicPath
from google.api_core.exceptions import GoogleAPICallError

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def mock_publishers():
    return {Partition(i): MagicMock(spec=Publisher) for i in range(10)}


@pytest.fixture()
def topic():
    return TopicPath.parse("projects/1/locations/us-central1-a/topics/topic")


@pytest.fixture()
def mock_admin():
    admin = MagicMock(spec=AdminClientInterface)
    return admin


@pytest.fixture()
def watcher(mock_admin, topic):
    return run_on_thread(lambda: PartitionCountWatcherImpl(mock_admin, topic, 0.001))


async def test_init(watcher, mock_admin, topic):
    mock_admin.get_topic_partition_count.return_value = 2
    async with watcher:
        pass


async def test_get_count_first_failure(watcher, mock_admin, topic):
    mock_admin.get_topic_partition_count.side_effect = GoogleAPICallError("error")
    with pytest.raises(GoogleAPICallError):
        async with watcher:
            await watcher.get_partition_count()


async def test_get_multiple_counts(watcher, mock_admin, topic):
    q = queue.Queue()
    mock_admin.get_topic_partition_count.side_effect = q.get
    async with watcher:
        task1 = asyncio.ensure_future(watcher.get_partition_count())
        task2 = asyncio.ensure_future(watcher.get_partition_count())
        assert not task1.done()
        assert not task2.done()
        q.put(3)
        assert await task1 == 3
        assert not task2.done()
        q.put(4)
        assert await task2 == 4


async def test_subsequent_failures_ignored(watcher, mock_admin, topic):
    q = queue.Queue()

    def side_effect():
        value = q.get()
        if isinstance(value, Exception):
            raise value
        return value

    mock_admin.get_topic_partition_count.side_effect = lambda x: side_effect()
    async with watcher:
        q.put(3)
        assert await watcher.get_partition_count() == 3
        q.put(GoogleAPICallError("error"))
        q.put(4)
        assert await watcher.get_partition_count() == 4
