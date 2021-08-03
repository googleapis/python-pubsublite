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
import json
from typing import Callable

from asynctest.mock import MagicMock, call
import pytest
from google.api_core.exceptions import FailedPrecondition
from google.cloud.pubsub_v1.subscriber.message import Message
from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.types import FlowControlSettings
from google.cloud.pubsublite.cloudpubsub.internal.ack_set_tracker import AckSetTracker
from google.cloud.pubsublite.cloudpubsub.internal.single_partition_subscriber import (
    SinglePartitionSingleSubscriber,
)
from google.cloud.pubsublite.cloudpubsub.message_transformer import MessageTransformer
from google.cloud.pubsublite.cloudpubsub.nack_handler import NackHandler
from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSingleSubscriber,
)
from google.cloud.pubsublite.internal.wire.subscriber import Subscriber
from google.cloud.pubsublite.internal.wire.subscriber_reset_handler import (
    SubscriberResetHandler,
)
from google.cloud.pubsublite.testing.test_utils import make_queue_waiter
from google.cloud.pubsublite_v1 import Cursor, FlowControlRequest, SequencedMessage

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


def mock_async_context_manager(cm):
    cm.__aenter__.return_value = cm
    return cm


def ack_id(generation, offset) -> str:
    return json.dumps({"generation": generation, "offset": offset})


@pytest.fixture()
def underlying():
    return mock_async_context_manager(MagicMock(spec=Subscriber))


@pytest.fixture()
def flow_control_settings():
    return FlowControlSettings(1000, 1000)


@pytest.fixture()
def initial_flow_request(flow_control_settings):
    return FlowControlRequest(
        allowed_messages=flow_control_settings.messages_outstanding,
        allowed_bytes=flow_control_settings.bytes_outstanding,
    )


@pytest.fixture()
def ack_set_tracker():
    return mock_async_context_manager(MagicMock(spec=AckSetTracker))


@pytest.fixture()
def nack_handler():
    return MagicMock(spec=NackHandler)


@pytest.fixture()
def transformer():
    result = MagicMock(spec=MessageTransformer)
    result.transform.side_effect = lambda source: PubsubMessage(
        message_id=str(source.cursor.offset)
    )
    return result


@pytest.fixture()
def subscriber(
    underlying, flow_control_settings, ack_set_tracker, nack_handler, transformer
):
    def subscriber_factory(reset_handler: SubscriberResetHandler):
        return underlying

    return SinglePartitionSingleSubscriber(
        subscriber_factory,
        flow_control_settings,
        ack_set_tracker,
        nack_handler,
        transformer,
    )


async def test_init(subscriber, underlying, ack_set_tracker, initial_flow_request):
    async with subscriber:
        underlying.__aenter__.assert_called_once()
        ack_set_tracker.__aenter__.assert_called_once()
        underlying.allow_flow.assert_called_once_with(initial_flow_request)
    underlying.__aexit__.assert_called_once()
    ack_set_tracker.__aexit__.assert_called_once()


async def test_failed_transform(subscriber, underlying, transformer):
    async with subscriber:
        transformer.transform.side_effect = FailedPrecondition("Bad message")
        underlying.read.return_value = SequencedMessage()
        with pytest.raises(FailedPrecondition):
            await subscriber.read()


async def test_ack(
    subscriber: AsyncSingleSubscriber, underlying, transformer, ack_set_tracker
):
    ack_called_queue = asyncio.Queue()
    ack_result_queue = asyncio.Queue()
    ack_set_tracker.ack.side_effect = make_queue_waiter(
        ack_called_queue, ack_result_queue
    )
    async with subscriber:
        message_1 = SequencedMessage(cursor=Cursor(offset=1), size_bytes=5)
        message_2 = SequencedMessage(cursor=Cursor(offset=2), size_bytes=10)
        underlying.read.return_value = message_1
        read_1: Message = await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1)])
        assert read_1.message_id == "1"
        underlying.read.return_value = message_2
        read_2: Message = await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1), call(2)])
        assert read_2.message_id == "2"
        read_2.ack()
        await ack_called_queue.get()
        await ack_result_queue.put(None)
        ack_set_tracker.ack.assert_has_calls([call(2)])
        read_1.ack()
        await ack_called_queue.get()
        await ack_result_queue.put(None)
        ack_set_tracker.ack.assert_has_calls([call(2), call(1)])


async def test_track_failure(
    subscriber: SinglePartitionSingleSubscriber,
    underlying,
    transformer,
    ack_set_tracker,
):
    async with subscriber:
        ack_set_tracker.track.side_effect = FailedPrecondition("Bad track")
        message = SequencedMessage(cursor=Cursor(offset=1), size_bytes=5)
        underlying.read.return_value = message
        with pytest.raises(FailedPrecondition):
            await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1)])


async def test_ack_failure(
    subscriber: SinglePartitionSingleSubscriber,
    underlying,
    transformer,
    ack_set_tracker,
):
    ack_called_queue = asyncio.Queue()
    ack_result_queue = asyncio.Queue()
    ack_set_tracker.ack.side_effect = make_queue_waiter(
        ack_called_queue, ack_result_queue
    )
    async with subscriber:
        message = SequencedMessage(cursor=Cursor(offset=1), size_bytes=5)
        underlying.read.return_value = message
        read: Message = await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1)])
        read.ack()
        await ack_called_queue.get()
        ack_set_tracker.ack.assert_has_calls([call(1)])
        await ack_result_queue.put(FailedPrecondition("Bad ack"))

        async def sleep_forever():
            await asyncio.sleep(float("inf"))

        underlying.read.side_effect = sleep_forever
        with pytest.raises(FailedPrecondition):
            await subscriber.read()


async def test_nack_failure(
    subscriber: SinglePartitionSingleSubscriber,
    underlying,
    transformer,
    ack_set_tracker,
    nack_handler,
):
    async with subscriber:
        message = SequencedMessage(cursor=Cursor(offset=1), size_bytes=5)
        underlying.read.return_value = message
        read: Message = await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1)])
        nack_handler.on_nack.side_effect = FailedPrecondition("Bad nack")
        read.nack()

        async def sleep_forever():
            await asyncio.sleep(float("inf"))

        underlying.read.side_effect = sleep_forever
        with pytest.raises(FailedPrecondition):
            await subscriber.read()


async def test_nack_calls_ack(
    subscriber: SinglePartitionSingleSubscriber,
    underlying,
    transformer,
    ack_set_tracker,
    nack_handler,
):
    ack_called_queue = asyncio.Queue()
    ack_result_queue = asyncio.Queue()
    ack_set_tracker.ack.side_effect = make_queue_waiter(
        ack_called_queue, ack_result_queue
    )
    async with subscriber:
        message = SequencedMessage(cursor=Cursor(offset=1), size_bytes=5)
        underlying.read.return_value = message
        read: Message = await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1)])

        def on_nack(nacked: PubsubMessage, ack: Callable[[], None]):
            assert nacked.message_id == "1"
            ack()

        nack_handler.on_nack.side_effect = on_nack
        read.nack()
        await ack_called_queue.get()
        await ack_result_queue.put(None)
        ack_set_tracker.ack.assert_has_calls([call(1)])


async def test_handle_reset(
    subscriber: SinglePartitionSingleSubscriber,
    underlying,
    transformer,
    ack_set_tracker,
):
    ack_called_queue = asyncio.Queue()
    ack_result_queue = asyncio.Queue()
    ack_set_tracker.ack.side_effect = make_queue_waiter(
        ack_called_queue, ack_result_queue
    )
    async with subscriber:
        message_1 = SequencedMessage(cursor=Cursor(offset=1), size_bytes=5)
        underlying.read.return_value = message_1
        read_1: Message = await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1)])
        assert read_1.message_id == "1"
        assert read_1.ack_id == ack_id(0, 1)

        await subscriber.handle_reset()
        ack_set_tracker.clear_and_commit.assert_called_once()

        # Message ACKed after reset. Its flow control tokens are refilled
        # but offset not committed (verified below after message 2).
        read_1.ack()

        message_2 = SequencedMessage(cursor=Cursor(offset=2), size_bytes=10)
        underlying.read.return_value = message_2
        read_2: Message = await subscriber.read()
        ack_set_tracker.track.assert_has_calls([call(1), call(2)])
        assert read_2.message_id == "2"
        assert read_2.ack_id == ack_id(1, 2)
        read_2.ack()
        await ack_called_queue.get()
        await ack_result_queue.put(None)
        underlying.allow_flow.assert_has_calls(
            [
                call(FlowControlRequest(allowed_messages=1000, allowed_bytes=1000,)),
                call(FlowControlRequest(allowed_messages=1, allowed_bytes=5,)),
                call(FlowControlRequest(allowed_messages=1, allowed_bytes=10,)),
            ]
        )
        ack_set_tracker.ack.assert_has_calls([call(2)])
