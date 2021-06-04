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

from asynctest.mock import MagicMock, CoroutineMock
import pytest
from google.api_core.exceptions import InternalServerError, InvalidArgument
from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    ConnectionFactory,
)
from google.cloud.pubsublite.internal.wire.connection_reinitializer import (
    ConnectionReinitializer,
)
from google.cloud.pubsublite.internal.wire.retrying_connection import (
    RetryingConnection,
    _MIN_BACKOFF_SECS,
)
from google.cloud.pubsublite.testing.test_utils import wire_queues

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.fixture()
def reinitializer():
    return MagicMock(spec=ConnectionReinitializer)


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
def retrying_connection(connection_factory, reinitializer):
    return RetryingConnection(connection_factory, reinitializer)


@pytest.fixture
def asyncio_sleep(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""
    mock = CoroutineMock()
    monkeypatch.setattr(asyncio, "sleep", mock)
    return mock


async def test_permanent_error_on_reinitializer(
    retrying_connection: Connection[int, int], reinitializer, default_connection
):
    async def reinit_action(conn, last_error):
        assert conn == default_connection
        assert last_error is None
        raise InvalidArgument("abc")

    reinitializer.reinitialize.side_effect = reinit_action
    with pytest.raises(InvalidArgument):
        async with retrying_connection as _:
            pass


async def test_successful_reinitialize(
    retrying_connection: Connection[int, int], reinitializer, default_connection
):
    async def reinit_action(conn, last_error):
        assert conn == default_connection
        assert last_error is None
        return None

    default_connection.read.return_value = 1

    reinitializer.reinitialize.side_effect = reinit_action
    async with retrying_connection as _:
        assert await retrying_connection.read() == 1
        assert (
            default_connection.read.call_count == 2
        )  # re-call to read once first completes
        write_fut = asyncio.Future()

        async def write_action(val: int):
            assert val == 2
            write_fut.set_result(None)

        default_connection.write.side_effect = write_action
        await retrying_connection.write(2)
        await write_fut
        default_connection.write.assert_called_once()


async def test_reinitialize_after_retryable(
    retrying_connection: Connection[int, int],
    reinitializer,
    default_connection,
    asyncio_sleep,
):
    reinit_queues = wire_queues(reinitializer.reinitialize)

    default_connection.read.return_value = 1

    error = InternalServerError("abc")
    await reinit_queues.results.put(error)
    await reinit_queues.results.put(None)
    async with retrying_connection as _:
        asyncio_sleep.assert_called_once_with(_MIN_BACKOFF_SECS)
        assert reinitializer.reinitialize.call_count == 2
        reinitializer.reinitialize.assert_has_calls(
            [call(default_connection, None), call(default_connection, error)]
        )
        assert await retrying_connection.read() == 1
        assert (
            default_connection.read.call_count == 2
        )  # re-call to read once first completes
