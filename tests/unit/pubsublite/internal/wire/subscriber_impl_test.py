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
from unittest.mock import call
from collections import defaultdict
from typing import Dict, List

from asynctest.mock import MagicMock, CoroutineMock
import pytest
from grpc import StatusCode

from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    ConnectionFactory,
)
from google.api_core.exceptions import InternalServerError, GoogleAPICallError

from google.cloud.pubsublite.internal.wire.subscriber import Subscriber
from google.cloud.pubsublite.internal.wire.subscriber_impl import SubscriberImpl
from google.cloud.pubsublite_v1 import (
    SubscribeRequest,
    SubscribeResponse,
    InitialSubscribeRequest,
    FlowControlRequest,
    SeekRequest,
)
from google.cloud.pubsublite_v1.types.common import Cursor, SequencedMessage
from google.cloud.pubsublite.testing.test_utils import make_queue_waiter
from google.cloud.pubsublite.internal.wire.retrying_connection import _MIN_BACKOFF_SECS

FLUSH_SECONDS = 100000

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.fixture()
def default_connection():
    conn = MagicMock(spec=Connection)
    conn.__aenter__.return_value = conn
    return conn


@pytest.fixture()
def connection_factory(default_connection):
    factory = MagicMock(spec=ConnectionFactory)
    factory.new.return_value = default_connection
    return factory


@pytest.fixture()
def initial_request():
    return SubscribeRequest(initial=InitialSubscribeRequest(subscription="mysub"))


class QueuePair:
    called: asyncio.Queue
    results: asyncio.Queue

    def __init__(self):
        self.called = asyncio.Queue()
        self.results = asyncio.Queue()


@pytest.fixture
def sleep_queues() -> Dict[float, QueuePair]:
    return defaultdict(QueuePair)


@pytest.fixture
def asyncio_sleep(monkeypatch, sleep_queues):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""
    mock = CoroutineMock()
    monkeypatch.setattr(asyncio, "sleep", mock)

    async def sleeper(delay: float):
        await make_queue_waiter(
            sleep_queues[delay].called, sleep_queues[delay].results
        )(delay)

    mock.side_effect = sleeper
    return mock


@pytest.fixture()
def subscriber(connection_factory, initial_request):
    return SubscriberImpl(initial_request.initial, FLUSH_SECONDS, connection_factory)


def as_request(flow: FlowControlRequest):
    req = SubscribeRequest()
    req.flow_control = flow
    return req


def as_response(messages: List[SequencedMessage]):
    res = SubscribeResponse()
    res.messages.messages = messages
    return res


async def test_basic_flow_control_after_timeout(
    subscriber: Subscriber,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    write_called_queue = asyncio.Queue()
    write_result_queue = asyncio.Queue()
    flow_1 = FlowControlRequest(allowed_messages=100, allowed_bytes=100)
    flow_2 = FlowControlRequest(allowed_messages=5, allowed_bytes=10)
    flow_3 = FlowControlRequest(allowed_messages=10, allowed_bytes=5)
    default_connection.write.side_effect = make_queue_waiter(
        write_called_queue, write_result_queue
    )
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    read_result_queue.put_nowait(SubscribeResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with subscriber:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Send tokens.
        flow_fut1 = asyncio.ensure_future(subscriber.allow_flow(flow_1))
        assert not flow_fut1.done()

        # Handle the inline write since initial tokens are 100% of outstanding.
        await write_called_queue.get()
        await write_result_queue.put(None)
        await flow_fut1
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(flow_1))]
        )

        # Should complete without writing to the connection
        await subscriber.allow_flow(flow_2)
        await subscriber.allow_flow(flow_3)

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        # Called with aggregate
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_request(flow_1)),
                call(
                    as_request(
                        FlowControlRequest(allowed_messages=15, allowed_bytes=15)
                    )
                ),
            ]
        )


async def test_flow_resent_on_restart(
    subscriber: Subscriber,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    write_called_queue = asyncio.Queue()
    write_result_queue = asyncio.Queue()
    flow_1 = FlowControlRequest(allowed_messages=100, allowed_bytes=100)
    flow_2 = FlowControlRequest(allowed_messages=5, allowed_bytes=10)
    flow_3 = FlowControlRequest(allowed_messages=10, allowed_bytes=5)
    default_connection.write.side_effect = make_queue_waiter(
        write_called_queue, write_result_queue
    )
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    read_result_queue.put_nowait(SubscribeResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with subscriber:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Send tokens.
        flow_fut1 = asyncio.ensure_future(subscriber.allow_flow(flow_1))
        assert not flow_fut1.done()

        # Handle the inline write since initial tokens are 100% of outstanding.
        await write_called_queue.get()
        await write_result_queue.put(None)
        await flow_fut1
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(flow_1))]
        )

        # Should complete without writing to the connection
        await subscriber.allow_flow(flow_2)
        await subscriber.allow_flow(flow_3)

        # Fail the connection with a retryable error
        await read_called_queue.get()
        await read_result_queue.put(InternalServerError("retryable"))
        await sleep_queues[_MIN_BACKOFF_SECS].called.get()
        await sleep_queues[_MIN_BACKOFF_SECS].results.put(None)
        # Reinitialization
        await write_called_queue.get()
        await write_result_queue.put(None)
        await read_called_queue.get()
        await read_result_queue.put(SubscribeResponse(initial={}))
        # Re-sending flow tokens on the new stream
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_request(flow_1)),
                call(initial_request),
                call(
                    as_request(
                        FlowControlRequest(allowed_messages=115, allowed_bytes=115)
                    )
                ),
            ]
        )


async def test_message_receipt(
    subscriber: Subscriber,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    write_called_queue = asyncio.Queue()
    write_result_queue = asyncio.Queue()
    flow = FlowControlRequest(allowed_messages=100, allowed_bytes=100)
    message_1 = SequencedMessage(cursor=Cursor(offset=3), size_bytes=5)
    message_2 = SequencedMessage(cursor=Cursor(offset=5), size_bytes=10)
    default_connection.write.side_effect = make_queue_waiter(
        write_called_queue, write_result_queue
    )
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    read_result_queue.put_nowait(SubscribeResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with subscriber:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Send tokens.
        flow_fut = asyncio.ensure_future(subscriber.allow_flow(flow))
        assert not flow_fut.done()

        # Handle the inline write since initial tokens are 100% of outstanding.
        await write_called_queue.get()
        await write_result_queue.put(None)
        await flow_fut
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(flow))]
        )

        message1_fut = asyncio.ensure_future(subscriber.read())

        # Send messages to the subscriber.
        await read_result_queue.put(as_response([message_1, message_2]))
        # Wait for the next read call
        await read_called_queue.get()

        assert (await message1_fut) == message_1
        assert (await subscriber.read()) == message_2

        # Fail the connection with a retryable error
        await read_called_queue.get()
        await read_result_queue.put(InternalServerError("retryable"))
        await sleep_queues[_MIN_BACKOFF_SECS].called.get()
        await sleep_queues[_MIN_BACKOFF_SECS].results.put(None)
        # Reinitialization
        await write_called_queue.get()
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(flow)), call(initial_request)]
        )
        await write_result_queue.put(None)
        await read_called_queue.get()
        await read_result_queue.put(SubscribeResponse(initial={}))
        # Sends fetch offset seek on the stream, and checks the response.
        seek_req = SubscribeRequest(
            seek=SeekRequest(cursor=Cursor(offset=message_2.cursor.offset + 1))
        )
        await write_called_queue.get()
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_request(flow)),
                call(initial_request),
                call(seek_req),
            ]
        )
        await write_result_queue.put(None)
        await read_called_queue.get()
        await read_result_queue.put(SubscribeResponse(seek={}))
        # Re-sending flow tokens on the new stream.
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_request(flow)),
                call(initial_request),
                call(seek_req),
                call(
                    as_request(
                        FlowControlRequest(allowed_messages=98, allowed_bytes=85)
                    )
                ),
            ]
        )


async def test_out_of_order_receipt_failure(
    subscriber: Subscriber,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    write_called_queue = asyncio.Queue()
    write_result_queue = asyncio.Queue()
    flow = FlowControlRequest(allowed_messages=100, allowed_bytes=100)
    message_1 = SequencedMessage(cursor=Cursor(offset=3), size_bytes=5)
    message_2 = SequencedMessage(cursor=Cursor(offset=5), size_bytes=10)
    default_connection.write.side_effect = make_queue_waiter(
        write_called_queue, write_result_queue
    )
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    read_result_queue.put_nowait(SubscribeResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with subscriber:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Send tokens.
        flow_fut = asyncio.ensure_future(subscriber.allow_flow(flow))
        assert not flow_fut.done()

        # Handle the inline write since initial tokens are 100% of outstanding.
        await write_called_queue.get()
        await write_result_queue.put(None)
        await flow_fut
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(flow))]
        )

        read_fut = asyncio.ensure_future(subscriber.read())

        # Send out of order messages to the subscriber.
        await read_result_queue.put(as_response([message_2, message_1]))
        # Wait for the next read call
        await read_called_queue.get()

        try:
            await read_fut
            assert False
        except GoogleAPICallError as e:
            assert e.grpc_status_code == StatusCode.FAILED_PRECONDITION
        pass
