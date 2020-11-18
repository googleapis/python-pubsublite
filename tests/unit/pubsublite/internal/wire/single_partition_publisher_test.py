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
def publisher(connection_factory, initial_request):
    return SinglePartitionPublisher(
        initial_request.initial_request, BATCHING_SETTINGS, connection_factory
    )


def as_publish_request(messages: List[PubSubMessage]):
    req = PublishRequest()
    req.message_publish_request.messages = messages
    return req


def as_publish_response(start_cursor: int):
    return PublishResponse(
        message_response=MessagePublishResponse(
            start_cursor=Cursor(offset=start_cursor)
        )
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
        await read_result_queue.put(as_publish_response(100))
        cursor1 = (await publish_fut1).cursor
        cursor2 = (await publish_fut2).cursor
        assert cursor1.offset == 100
        assert cursor2.offset == 101


async def test_publishes_multi_cycle(
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

        # Send the connection responses
        await read_result_queue.put(as_publish_response(100))
        cursor1 = (await publish_fut1).cursor
        assert cursor1.offset == 100
        assert not publish_fut2.done()
        await read_result_queue.put(as_publish_response(105))
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
