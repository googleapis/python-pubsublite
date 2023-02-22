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
from unittest.mock import AsyncMock, call, MagicMock
from collections import defaultdict
from typing import Dict, List, Optional

import pytest
from google.cloud.pubsub_v1.types import BatchSettings

from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    ConnectionFactory,
)
from google.api_core.exceptions import InternalServerError
from google.cloud.pubsublite_v1.types.publisher import (
    InitialPublishRequest,
    PublishRequest,
    PublishResponse,
    MessagePublishResponse,
)
from google.cloud.pubsublite_v1.types.common import PubSubMessage, Cursor
from google.cloud.pubsublite.internal.publish_sequence_number import (
    PublishSequenceNumber,
)
from google.cloud.pubsublite.internal.wire.single_partition_publisher import (
    SinglePartitionPublisher,
)
from google.cloud.pubsublite.internal.wire.publisher import Publisher
from google.cloud.pubsublite.testing.test_utils import make_queue_waiter
from google.cloud.pubsublite.internal.wire.retrying_connection import _MIN_BACKOFF_SECS

FLUSH_SECONDS = 100000
BATCHING_SETTINGS = BatchSettings(
    max_bytes=3 * 1024 * 1024, max_messages=1000, max_latency=FLUSH_SECONDS
)

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

CursorRange = MessagePublishResponse.CursorRange


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
    return PublishRequest(initial_request=InitialPublishRequest(topic="mytopic"))


@pytest.fixture()
def initial_request_with_client_id():
    return PublishRequest(
        initial_request=InitialPublishRequest(topic="mytopic", client_id=b"publisher")
    )


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
    mock_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    async def sleeper(delay: float):
        await make_queue_waiter(
            sleep_queues[delay].called, sleep_queues[delay].results
        )(delay)

    mock_sleep.side_effect = sleeper
    return mock_sleep


@pytest.fixture()
def publisher(connection_factory, initial_request):
    return SinglePartitionPublisher(
        initial_request.initial_request,
        BATCHING_SETTINGS,
        connection_factory,
        PublishSequenceNumber(0),
    )


@pytest.fixture
def initial_sequence():
    return PublishSequenceNumber(514)


@pytest.fixture()
def idempotent_publisher(
    connection_factory, initial_request_with_client_id, initial_sequence
):
    return SinglePartitionPublisher(
        initial_request_with_client_id.initial_request,
        BATCHING_SETTINGS,
        connection_factory,
        initial_sequence,
    )


def as_publish_request(
    messages: List[PubSubMessage],
    first_sequence: Optional[PublishSequenceNumber] = None,
):
    req = PublishRequest()
    req.message_publish_request.messages = messages
    if first_sequence:
        req.message_publish_request.first_sequence_number = first_sequence.value
    return req


def cursor_range(start_offset, start_index, end_index: int):
    return CursorRange(
        start_cursor=Cursor(offset=start_offset),
        start_index=start_index,
        end_index=end_index,
    )


def as_publish_response(cursor_ranges: List[CursorRange]):
    return PublishResponse(
        message_response=MessagePublishResponse(cursor_ranges=cursor_ranges)
    )


async def test_basic_publish_after_timeout(
    publisher: Publisher,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    message1 = PubSubMessage(data=b"abc")
    message2 = PubSubMessage(data=b"def")
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    read_result_queue.put_nowait(PublishResponse(initial_response={}))
    async with publisher:
        # Set up connection
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Write messages
        publish_fut1 = asyncio.ensure_future(publisher.publish(message1))
        publish_fut2 = asyncio.ensure_future(publisher.publish(message2))
        assert not publish_fut1.done()
        assert not publish_fut2.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        write_future = asyncio.Future()

        async def write(val: PublishRequest):
            write_future.set_result(None)

        default_connection.write.side_effect = write
        await sleep_results.put(None)
        await write_future
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_publish_request([message1, message2]))]
        )
        assert not publish_fut1.done()
        assert not publish_fut2.done()

        # Send the connection response
        await read_result_queue.put(as_publish_response([cursor_range(100, 0, 2)]))
        cursor1 = (await publish_fut1).cursor
        cursor2 = (await publish_fut2).cursor
        assert cursor1.offset == 100
        assert cursor2.offset == 101


async def test_publishes_multi_cycle(
    idempotent_publisher: Publisher,
    default_connection,
    initial_request_with_client_id,
    initial_sequence,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    message1 = PubSubMessage(data=b"abc")
    message2 = PubSubMessage(data=b"def")
    write_called_queue = asyncio.Queue()
    write_result_queue = asyncio.Queue()
    default_connection.write.side_effect = make_queue_waiter(
        write_called_queue, write_result_queue
    )
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    write_result_queue.put_nowait(None)
    read_result_queue.put_nowait(PublishResponse(initial_response={}))
    async with idempotent_publisher:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls(
            [call(initial_request_with_client_id)]
        )

        # Write message 1
        publish_fut1 = asyncio.ensure_future(idempotent_publisher.publish(message1))
        assert not publish_fut1.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [
                call(initial_request_with_client_id),
                call(as_publish_request([message1], initial_sequence)),
            ]
        )
        assert not publish_fut1.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_has_calls([call(FLUSH_SECONDS), call(FLUSH_SECONDS)])

        # Write message 2
        publish_fut2 = asyncio.ensure_future(idempotent_publisher.publish(message2))
        assert not publish_fut2.done()

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [
                call(initial_request_with_client_id),
                call(as_publish_request([message1], initial_sequence)),
                call(
                    as_publish_request(
                        [message2], PublishSequenceNumber(initial_sequence.value + 1)
                    )
                ),
            ]
        )
        assert not publish_fut1.done()
        assert not publish_fut2.done()

        # Send the connection responses
        await read_result_queue.put(as_publish_response([cursor_range(100, 0, 1)]))
        cursor1 = (await publish_fut1).cursor
        assert cursor1.offset == 100
        assert not publish_fut2.done()
        await read_result_queue.put(as_publish_response([cursor_range(105, 0, 1)]))
        cursor2 = (await publish_fut2).cursor
        assert cursor2.offset == 105


async def test_publishes_retried_on_restart(
    publisher: Publisher,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    message1 = PubSubMessage(data=b"abc")
    message2 = PubSubMessage(data=b"def")
    write_called_queue = asyncio.Queue()
    write_result_queue = asyncio.Queue()
    default_connection.write.side_effect = make_queue_waiter(
        write_called_queue, write_result_queue
    )
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    write_result_queue.put_nowait(None)
    read_result_queue.put_nowait(PublishResponse(initial_response={}))
    async with publisher:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Write message 1
        publish_fut1 = asyncio.ensure_future(publisher.publish(message1))
        assert not publish_fut1.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_publish_request([message1]))]
        )
        assert not publish_fut1.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_has_calls([call(FLUSH_SECONDS), call(FLUSH_SECONDS)])

        # Write message 2
        publish_fut2 = asyncio.ensure_future(publisher.publish(message2))
        assert not publish_fut2.done()

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_publish_request([message1])),
                call(as_publish_request([message2])),
            ]
        )
        assert not publish_fut1.done()
        assert not publish_fut2.done()

        # Fail the connection with a retryable error
        await read_called_queue.get()
        await read_result_queue.put(InternalServerError("retryable"))
        await sleep_queues[_MIN_BACKOFF_SECS].called.get()
        await sleep_queues[_MIN_BACKOFF_SECS].results.put(None)
        # Reinitialization
        await write_called_queue.get()
        write_result_queue.put_nowait(None)
        await read_called_queue.get()
        read_result_queue.put_nowait(PublishResponse(initial_response={}))
        # Re-sending messages on the new stream
        await write_called_queue.get()
        await write_result_queue.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        asyncio_sleep.assert_has_calls(
            [
                call(FLUSH_SECONDS),
                call(FLUSH_SECONDS),
                call(FLUSH_SECONDS),
                call(_MIN_BACKOFF_SECS),
            ]
        )
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_publish_request([message1])),
                call(as_publish_request([message2])),
                call(initial_request),
                call(as_publish_request([message1])),
                call(as_publish_request([message2])),
            ]
        )


async def test_missing_cursor_ranges(
    idempotent_publisher: Publisher,
    default_connection,
    initial_request_with_client_id,
    initial_sequence,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    message1 = PubSubMessage(data=b"msg1")
    message2 = PubSubMessage(data=b"msg2")
    message3 = PubSubMessage(data=b"msg3")
    message4 = PubSubMessage(data=b"msg4")
    message5 = PubSubMessage(data=b"msg5")
    message6 = PubSubMessage(data=b"msg6")
    message7 = PubSubMessage(data=b"msg7")
    read_called_queue = asyncio.Queue()
    read_result_queue = asyncio.Queue()
    default_connection.read.side_effect = make_queue_waiter(
        read_called_queue, read_result_queue
    )
    read_result_queue.put_nowait(PublishResponse(initial_response={}))
    async with idempotent_publisher:
        # Set up connection
        await read_called_queue.get()
        default_connection.write.assert_has_calls(
            [call(initial_request_with_client_id)]
        )

        # Write messages
        publish_fut1 = asyncio.ensure_future(idempotent_publisher.publish(message1))
        publish_fut2 = asyncio.ensure_future(idempotent_publisher.publish(message2))
        publish_fut3 = asyncio.ensure_future(idempotent_publisher.publish(message3))
        publish_fut4 = asyncio.ensure_future(idempotent_publisher.publish(message4))
        publish_fut5 = asyncio.ensure_future(idempotent_publisher.publish(message5))
        publish_fut6 = asyncio.ensure_future(idempotent_publisher.publish(message6))
        publish_fut7 = asyncio.ensure_future(idempotent_publisher.publish(message7))

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        write_future = asyncio.Future()

        async def write(val: PublishRequest):
            write_future.set_result(None)

        default_connection.write.side_effect = write
        await sleep_results.put(None)
        await write_future
        default_connection.write.assert_has_calls(
            [
                call(initial_request_with_client_id),
                call(
                    as_publish_request(
                        [
                            message1,
                            message2,
                            message3,
                            message4,
                            message5,
                            message6,
                            message7,
                        ],
                        initial_sequence,
                    )
                ),
            ]
        )
        assert not publish_fut1.done()
        assert not publish_fut2.done()
        assert not publish_fut3.done()
        assert not publish_fut4.done()
        assert not publish_fut5.done()
        assert not publish_fut6.done()
        assert not publish_fut7.done()

        # Send the connection response
        # The server should not respond with unsorted cursor ranges, but check
        # that it is handled.
        await read_result_queue.put(
            as_publish_response(
                [
                    cursor_range(50, 4, 5),
                    cursor_range(80, 5, 6),
                    cursor_range(10, 1, 3),
                ]
            )
        )
        cursor1 = (await publish_fut1).cursor
        cursor2 = (await publish_fut2).cursor
        cursor3 = (await publish_fut3).cursor
        cursor4 = (await publish_fut4).cursor
        cursor5 = (await publish_fut5).cursor
        cursor6 = (await publish_fut6).cursor
        cursor7 = (await publish_fut7).cursor
        assert cursor1.offset == -1
        assert cursor2.offset == 10
        assert cursor3.offset == 11
        assert cursor4.offset == -1
        assert cursor5.offset == 50
        assert cursor6.offset == 80
        assert cursor7.offset == -1
