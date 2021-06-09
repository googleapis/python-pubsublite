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
from typing import Dict

from asynctest.mock import MagicMock, CoroutineMock
import pytest

from google.cloud.pubsublite.internal.wire.committer import Committer
from google.cloud.pubsublite.internal.wire.committer_impl import CommitterImpl
from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    ConnectionFactory,
)
from google.api_core.exceptions import InternalServerError, InvalidArgument
from google.cloud.pubsublite_v1.types.cursor import (
    StreamingCommitCursorRequest,
    StreamingCommitCursorResponse,
    InitialCommitCursorRequest,
)
from google.cloud.pubsublite_v1.types.common import Cursor
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
    return StreamingCommitCursorRequest(
        initial=InitialCommitCursorRequest(subscription="mysub")
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
    mock = CoroutineMock()
    monkeypatch.setattr(asyncio, "sleep", mock)

    async def sleeper(delay: float):
        await make_queue_waiter(
            sleep_queues[delay].called, sleep_queues[delay].results
        )(delay)

    mock.side_effect = sleeper
    return mock


@pytest.fixture()
def committer(connection_factory, initial_request):
    return CommitterImpl(initial_request.initial, FLUSH_SECONDS, connection_factory)


def as_request(cursor: Cursor):
    req = StreamingCommitCursorRequest()
    req.commit.cursor = cursor
    return req


def as_response(count: int):
    res = StreamingCommitCursorResponse()
    res.commit.acknowledged_commits = count
    return res


async def test_basic_commit_after_timeout(
    committer: Committer,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    cursor1 = Cursor(offset=321)
    cursor2 = Cursor(offset=1)
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
    read_result_queue.put_nowait(StreamingCommitCursorResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with committer:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Commit cursors
        commit_fut1 = asyncio.ensure_future(committer.commit(cursor1))
        commit_fut2 = asyncio.ensure_future(committer.commit(cursor2))
        empty_fut = asyncio.ensure_future(committer.wait_until_empty())
        assert not commit_fut1.done()
        assert not commit_fut2.done()
        assert not empty_fut.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        # Called with second cursor
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(cursor2))]
        )
        assert not commit_fut1.done()
        assert not commit_fut2.done()
        assert not empty_fut.done()

        # Send the connection response with 1 ack since only one request was sent.
        await read_result_queue.put(as_response(count=1))
        await commit_fut1
        await commit_fut2
        await empty_fut


async def test_commits_multi_cycle(
    committer: Committer,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    cursor1 = Cursor(offset=321)
    cursor2 = Cursor(offset=1)
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
    read_result_queue.put_nowait(StreamingCommitCursorResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with committer:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Write message 1
        commit_fut1 = asyncio.ensure_future(committer.commit(cursor1))
        empty_fut = asyncio.ensure_future(committer.wait_until_empty())
        assert not commit_fut1.done()
        assert not empty_fut.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(cursor1))]
        )
        assert not commit_fut1.done()
        assert not empty_fut.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_has_calls([call(FLUSH_SECONDS), call(FLUSH_SECONDS)])

        # Write message 2
        commit_fut2 = asyncio.ensure_future(committer.commit(cursor2))
        assert not commit_fut2.done()
        assert not empty_fut.done()

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_request(cursor1)),
                call(as_request(cursor2)),
            ]
        )
        assert not commit_fut1.done()
        assert not commit_fut2.done()
        assert not empty_fut.done()

        # Send the connection responses
        await read_result_queue.put(as_response(count=2))
        await commit_fut1
        await commit_fut2
        await empty_fut


async def test_publishes_retried_on_restart(
    committer: Committer,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    cursor1 = Cursor(offset=321)
    cursor2 = Cursor(offset=1)
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
    read_result_queue.put_nowait(StreamingCommitCursorResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with committer:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Write message 1
        commit_fut1 = asyncio.ensure_future(committer.commit(cursor1))
        empty_fut = asyncio.ensure_future(committer.wait_until_empty())
        assert not commit_fut1.done()
        assert not empty_fut.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(cursor1))]
        )
        assert not commit_fut1.done()
        assert not empty_fut.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_has_calls([call(FLUSH_SECONDS), call(FLUSH_SECONDS)])

        # Write message 2
        commit_fut2 = asyncio.ensure_future(committer.commit(cursor2))
        assert not commit_fut2.done()
        assert not empty_fut.done()

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [
                call(initial_request),
                call(as_request(cursor1)),
                call(as_request(cursor2)),
            ]
        )
        assert not commit_fut1.done()
        assert not commit_fut2.done()
        assert not empty_fut.done()

        # Fail the connection with a retryable error
        await read_called_queue.get()
        await read_result_queue.put(InternalServerError("retryable"))
        await sleep_queues[_MIN_BACKOFF_SECS].called.get()
        await sleep_queues[_MIN_BACKOFF_SECS].results.put(None)
        # Reinitialization
        await write_called_queue.get()
        await write_result_queue.put(None)
        await read_called_queue.get()
        await read_result_queue.put(StreamingCommitCursorResponse(initial={}))
        # Re-sending messages on the new stream
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
                # Aggregates response calls on second pass
                call(initial_request),
                call(as_request(cursor2)),
            ]
        )
        assert not empty_fut.done()

        # Sending the response for the one commit finishes both
        await read_called_queue.get()
        await read_result_queue.put(as_response(count=1))
        await commit_fut1
        await commit_fut2
        await empty_fut


async def test_wait_until_empty_completes_on_failure(
    committer: Committer,
    default_connection,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
    sleep_called = sleep_queues[FLUSH_SECONDS].called
    sleep_results = sleep_queues[FLUSH_SECONDS].results
    cursor1 = Cursor(offset=1)
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
    read_result_queue.put_nowait(StreamingCommitCursorResponse(initial={}))
    write_result_queue.put_nowait(None)
    async with committer:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # New committer is empty.
        await committer.wait_until_empty()

        # Write message 1
        commit_fut1 = asyncio.ensure_future(committer.commit(cursor1))
        empty_fut = asyncio.ensure_future(committer.wait_until_empty())
        assert not commit_fut1.done()
        assert not empty_fut.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_called_with(FLUSH_SECONDS)

        # Handle the connection write
        await sleep_results.put(None)
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [call(initial_request), call(as_request(cursor1))]
        )
        assert not commit_fut1.done()
        assert not empty_fut.done()

        # Wait for writes to be waiting
        await sleep_called.get()
        asyncio_sleep.assert_has_calls([call(FLUSH_SECONDS), call(FLUSH_SECONDS)])

        # Fail the connection with a permanent error
        await read_called_queue.get()
        await read_result_queue.put(InvalidArgument("permanent"))

        with pytest.raises(InvalidArgument):
            await empty_fut
