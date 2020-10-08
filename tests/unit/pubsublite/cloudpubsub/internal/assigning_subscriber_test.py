from typing import Set

from asynctest.mock import MagicMock, call
import threading
import pytest
from google.api_core.exceptions import FailedPrecondition
from google.cloud.pubsub_v1.subscriber.message import Message
from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub.internal.assigning_subscriber import (
    AssigningSubscriber,
    PartitionSubscriberFactory,
)
from google.cloud.pubsublite.cloudpubsub.subscriber import AsyncSubscriber
from google.cloud.pubsublite.internal.wire.assigner import Assigner
from google.cloud.pubsublite.partition import Partition
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
        box.val = AssigningSubscriber(lambda: assigner, subscriber_factory)

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
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
        sub2 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
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
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
        sub2 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
        sub3 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
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
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
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
        sub1 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
        sub2 = mock_async_context_manager(MagicMock(spec=AsyncSubscriber))
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
