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
from typing import Dict, Set

from asynctest.mock import MagicMock, CoroutineMock
import pytest

from google.cloud.pubsublite.internal.wire.assigner import Assigner
from google.cloud.pubsublite.internal.wire.assigner_impl import AssignerImpl
from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    ConnectionFactory,
)
from google.api_core.exceptions import InternalServerError

from google.cloud.pubsublite.types import Partition
from google.cloud.pubsublite_v1.types.subscriber import (
    PartitionAssignmentRequest,
    InitialPartitionAssignmentRequest,
    PartitionAssignment,
    PartitionAssignmentAck,
)
from google.cloud.pubsublite.testing.test_utils import make_queue_waiter
from google.cloud.pubsublite.internal.wire.retrying_connection import _MIN_BACKOFF_SECS

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
    return PartitionAssignmentRequest(
        initial=InitialPartitionAssignmentRequest(subscription="mysub")
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
def assigner(connection_factory, initial_request):
    return AssignerImpl(initial_request.initial, connection_factory)


def as_response(partitions: Set[Partition]):
    req = PartitionAssignment()
    req.partitions = [partition.value for partition in partitions]
    return req


def ack_request():
    return PartitionAssignmentRequest(ack=PartitionAssignmentAck())


async def test_basic_assign(assigner: Assigner, default_connection, initial_request):
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
    async with assigner:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Wait for the first assignment
        assign_fut1 = asyncio.ensure_future(assigner.get_assignment())
        assert not assign_fut1.done()

        partitions = {Partition(2), Partition(7)}

        # Send the first assignment.
        await read_result_queue.put(as_response(partitions=partitions))
        assert (await assign_fut1) == partitions

        # Get the next assignment: should send an ack on the stream
        assign_fut2 = asyncio.ensure_future(assigner.get_assignment())
        await write_called_queue.get()
        await write_result_queue.put(None)
        default_connection.write.assert_has_calls(
            [call(initial_request), call(ack_request())]
        )

        partitions = {Partition(5)}

        # Send the second assignment.
        await read_called_queue.get()
        await read_result_queue.put(as_response(partitions=partitions))
        assert (await assign_fut2) == partitions


async def test_restart(
    assigner: Assigner,
    default_connection,
    connection_factory,
    initial_request,
    asyncio_sleep,
    sleep_queues,
):
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
    async with assigner:
        # Set up connection
        await write_called_queue.get()
        await read_called_queue.get()
        default_connection.write.assert_has_calls([call(initial_request)])

        # Wait for the first assignment
        assign_fut1 = asyncio.ensure_future(assigner.get_assignment())
        assert not assign_fut1.done()

        partitions = {Partition(2), Partition(7)}

        # Send the first assignment.
        await read_result_queue.put(as_response(partitions=partitions))
        await read_called_queue.get()
        assert (await assign_fut1) == partitions

        # Get the next assignment: should attempt to send an ack on the stream
        assign_fut2 = asyncio.ensure_future(assigner.get_assignment())
        await write_called_queue.get()
        default_connection.write.assert_has_calls(
            [call(initial_request), call(ack_request())]
        )

        # Set up the next connection
        conn2 = MagicMock(spec=Connection)
        conn2.__aenter__.return_value = conn2
        connection_factory.new.return_value = conn2
        write_called_queue_2 = asyncio.Queue()
        write_result_queue_2 = asyncio.Queue()
        conn2.write.side_effect = make_queue_waiter(
            write_called_queue_2, write_result_queue_2
        )
        read_called_queue_2 = asyncio.Queue()
        read_result_queue_2 = asyncio.Queue()
        conn2.read.side_effect = make_queue_waiter(
            read_called_queue_2, read_result_queue_2
        )

        # Fail the connection by failing the write call.
        await write_result_queue.put(InternalServerError("failed"))
        await sleep_queues[_MIN_BACKOFF_SECS].called.get()
        await sleep_queues[_MIN_BACKOFF_SECS].results.put(None)

        # Reinitialize
        await write_called_queue_2.get()
        write_result_queue_2.put_nowait(None)
        conn2.write.assert_has_calls([call(initial_request)])

        partitions = {Partition(5)}

        # Send the second assignment on the new connection.
        await read_called_queue_2.get()
        await read_result_queue_2.put(as_response(partitions=partitions))
        assert (await assign_fut2) == partitions
        # No ack call ever made.
        conn2.write.assert_has_calls([call(initial_request)])
