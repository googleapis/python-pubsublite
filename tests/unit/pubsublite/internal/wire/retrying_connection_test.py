import asyncio
from typing import Union

from asynctest.mock import MagicMock, CoroutineMock
from google.api_core.exceptions import InternalServerError, InvalidArgument
import pytest
from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    ConnectionFactory,
)
from google.cloud.pubsublite.internal.wire.connection_reinitializer import (
    ConnectionReinitializer,
)
from google.cloud.pubsublite.internal.wire.retrying_connection import (
    _MIN_BACKOFF_SECS,
    RetryingConnection,
)

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.fixture()
def reinitializer():
    return MagicMock(spec=ConnectionReinitializer[int, int])


@pytest.fixture()
def default_connection():
    conn = MagicMock(spec=Connection[int, int])
    conn.__aenter__.return_value = conn
    return conn


@pytest.fixture()
def connection_factory(default_connection):
    factory = MagicMock(spec=ConnectionFactory[int, int])
    factory.new.return_value = default_connection
    return factory


@pytest.fixture()
def retrying_connection(connection_factory, reinitializer):
    return RetryingConnection[int, int](connection_factory, reinitializer)


@pytest.fixture
def asyncio_sleep(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""
    mock = CoroutineMock()
    monkeypatch.setattr(asyncio, "sleep", mock)
    return mock


async def test_permanent_error_on_reinitializer(
    retrying_connection: Connection[int, int], reinitializer, default_connection
):
    fut = asyncio.Future()
    reinitialize_called = asyncio.Future()

    async def reinit_action(conn):
        assert conn == default_connection
        reinitialize_called.set_result(None)
        return await fut

    reinitializer.reinitialize.side_effect = reinit_action
    async with retrying_connection as _:
        await reinitialize_called
        reinitializer.reinitialize.assert_called_once()
        fut.set_exception(InvalidArgument("abc"))
        with pytest.raises(InvalidArgument):
            await retrying_connection.read()


async def test_successful_reinitialize(
    retrying_connection: Connection[int, int], reinitializer, default_connection
):
    fut = asyncio.Future()
    reinitialize_called = asyncio.Future()

    async def reinit_action(conn):
        assert conn == default_connection
        reinitialize_called.set_result(None)
        return await fut

    reinitializer.reinitialize.side_effect = reinit_action
    async with retrying_connection as _:
        await reinitialize_called
        reinitializer.reinitialize.assert_called_once()
        fut.set_result(None)
        default_connection.read.return_value = 1
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
    reinit_called = asyncio.Queue()
    reinit_results: "asyncio.Queue[Union[None, Exception]]" = asyncio.Queue()

    async def reinit_action(conn):
        assert conn == default_connection
        await reinit_called.put(None)
        result = await reinit_results.get()
        if isinstance(result, Exception):
            raise result

    reinitializer.reinitialize.side_effect = reinit_action
    async with retrying_connection as _:
        await reinit_called.get()
        reinitializer.reinitialize.assert_called_once()
        await reinit_results.put(InternalServerError("abc"))
        await reinit_called.get()
        asyncio_sleep.assert_called_once_with(_MIN_BACKOFF_SECS)
        assert reinitializer.reinitialize.call_count == 2
        await reinit_results.put(None)
        default_connection.read.return_value = 1
        assert await retrying_connection.read() == 1
        assert (
            default_connection.read.call_count == 2
        )  # re-call to read once first completes
