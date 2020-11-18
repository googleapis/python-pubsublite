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

from typing import Set

from asynctest.mock import MagicMock, call
import threading
import pytest
from google.api_core.exceptions import FailedPrecondition
from google.cloud.pubsub_v1.subscriber.message import Message
from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub.internal.assigning_subscriber import (
    AssigningSingleSubscriber,
    PartitionSubscriberFactory,
)
from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSingleSubscriber,
)
from google.cloud.pubsublite.internal.wire.assigner import Assigner
from google.cloud.pubsublite.types import Partition
from google.cloud.pubsublite.testing.test_utils import wire_queues, Box

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


def mock_async_context_manager(cm):
    cm.__aenter__.return_value = cm
    return cm


@pytest.fixture()
def assigner():
    return mock_async_context_manager(MagicMock(spec=Assigner))


@pytest.fixture()
def subscriber_factory():
    return MagicMock(spec=PartitionSubscriberFactory)


@pytest.fixture()
def subscriber(assigner, subscriber_factory):
    box = Box()

    def set_box():
        box.val = AssigningSingleSubscriber(lambda: assigner, subscriber_factory)

    # Initialize AssigningSubscriber on another thread with a different event loop.
    thread = threading.Thread(target=set_box)
    thread.start()
    thread.join()
    return box.val


async def test_init(subscriber, assigner):
    assign_queues = wire_queues(assigner.get_assignment)
    async with subscriber:
        assigner.__aenter__.assert_called_once()
        await assign_queues.called.get()
        assigner.get_assignment.assert_called_once()
    assigner.__aexit__.assert_called_once()


async def test_initial_assignment(subscriber, assigner, subscriber_factory):
    assign_queues = wire_queues(assigner.get_assignment)
    async with subscriber:
        await assign_queues.called.get()
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        sub2 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        subscriber_factory.side_effect = (
            lambda partition: sub1 if partition == Partition(1) else sub2
        )
        await assign_queues.results.put({Partition(1), Partition(2)})
        await assign_queues.called.get()
        subscriber_factory.assert_has_calls(
            [call(Partition(1)), call(Partition(2))], any_order=True
        )
        sub1.__aenter__.assert_called_once()
        sub2.__aenter__.assert_called_once()
    sub1.__aexit__.assert_called_once()
    sub2.__aexit__.assert_called_once()


async def test_assigner_failure(subscriber, assigner, subscriber_factory):
    assign_queues = wire_queues(assigner.get_assignment)
    async with subscriber:
        await assign_queues.called.get()
        await assign_queues.results.put(FailedPrecondition("bad assign"))
        with pytest.raises(FailedPrecondition):
            await subscriber.read()


async def test_assignment_change(subscriber, assigner, subscriber_factory):
    assign_queues = wire_queues(assigner.get_assignment)
    async with subscriber:
        await assign_queues.called.get()
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        sub2 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        sub3 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        subscriber_factory.side_effect = (
            lambda partition: sub1
            if partition == Partition(1)
            else sub2
            if partition == Partition(2)
            else sub3
        )
        await assign_queues.results.put({Partition(1), Partition(2)})
        await assign_queues.called.get()
        subscriber_factory.assert_has_calls(
            [call(Partition(1)), call(Partition(2))], any_order=True
        )
        sub1.__aenter__.assert_called_once()
        sub2.__aenter__.assert_called_once()
        await assign_queues.results.put({Partition(1), Partition(3)})
        await assign_queues.called.get()
        subscriber_factory.assert_has_calls(
            [call(Partition(1)), call(Partition(2)), call(Partition(3))], any_order=True
        )
        sub3.__aenter__.assert_called_once()
        sub2.__aexit__.assert_called_once()
    sub1.__aexit__.assert_called_once()
    sub2.__aexit__.assert_called_once()
    sub3.__aexit__.assert_called_once()


async def test_subscriber_failure(subscriber, assigner, subscriber_factory):
    assign_queues = wire_queues(assigner.get_assignment)
    async with subscriber:
        await assign_queues.called.get()
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        sub1_queues = wire_queues(sub1.read)
        subscriber_factory.return_value = sub1
        await assign_queues.results.put({Partition(1)})
        await sub1_queues.called.get()
        await sub1_queues.results.put(FailedPrecondition("sub failed"))
        with pytest.raises(FailedPrecondition):
            await subscriber.read()


async def test_delivery_from_multiple(subscriber, assigner, subscriber_factory):
    assign_queues = wire_queues(assigner.get_assignment)
    async with subscriber:
        await assign_queues.called.get()
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        sub2 = mock_async_context_manager(MagicMock(spec=AsyncSingleSubscriber))
        sub1_queues = wire_queues(sub1.read)
        sub2_queues = wire_queues(sub2.read)
        subscriber_factory.side_effect = (
            lambda partition: sub1 if partition == Partition(1) else sub2
        )
        await assign_queues.results.put({Partition(1), Partition(2)})
        await sub1_queues.results.put(
            Message(PubsubMessage(message_id="1")._pb, "", 0, None)
        )
        await sub2_queues.results.put(
            Message(PubsubMessage(message_id="2")._pb, "", 0, None)
        )
        message_ids: Set[str] = set()
        message_ids.add((await subscriber.read()).message_id)
        message_ids.add((await subscriber.read()).message_id)
        assert message_ids == {"1", "2"}
