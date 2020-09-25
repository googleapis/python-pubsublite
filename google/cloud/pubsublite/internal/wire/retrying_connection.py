import asyncio

from typing import Awaitable
from google.api_core.exceptions import GoogleAPICallError, Cancelled
from google.cloud.pubsublite.status_codes import is_retryable
from google.cloud.pubsublite.internal.wire.connection_reinitializer import (
    ConnectionReinitializer,
)
from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    Request,
    Response,
    ConnectionFactory,
)
from google.cloud.pubsublite.internal.wire.work_item import WorkItem
from google.cloud.pubsublite.internal.wire.permanent_failable import PermanentFailable

_MIN_BACKOFF_SECS = 0.01
_MAX_BACKOFF_SECS = 10


class RetryingConnection(Connection[Request, Response], PermanentFailable):
    """A connection which performs retries on an underlying stream when experiencing retryable errors."""

    _connection_factory: ConnectionFactory[Request, Response]
    _reinitializer: ConnectionReinitializer[Request, Response]

    _loop_task: asyncio.Future

    _write_queue: "asyncio.Queue[WorkItem[Request, None]]"
    _read_queue: "asyncio.Queue[Response]"

    def __init__(
        self,
        connection_factory: ConnectionFactory[Request, Response],
        reinitializer: ConnectionReinitializer[Request, Response],
    ):
        super().__init__()
        self._connection_factory = connection_factory
        self._reinitializer = reinitializer
        self._write_queue = asyncio.Queue(maxsize=1)
        self._read_queue = asyncio.Queue(maxsize=1)

    async def __aenter__(self):
        self._loop_task = asyncio.ensure_future(self._run_loop())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.fail(Cancelled("Connection shutting down."))

    async def write(self, request: Request) -> None:
        item = WorkItem(request)
        await self.await_or_fail(self._write_queue.put(item))
        return await self.await_or_fail(item.response_future)

    async def read(self) -> Response:
        return await self.await_or_fail(self._read_queue.get())

    async def _run_loop(self):
        """
        Processes actions on this connection and handles retries until cancelled.
        """
        try:
            bad_retries = 0
            while True:
                try:
                    async with self._connection_factory.new() as connection:
                        await self._reinitializer.reinitialize(connection)
                        bad_retries = 0
                        await self._loop_connection(connection)
                except GoogleAPICallError as e:
                    if not is_retryable(e):
                        self.fail(e)
                        return
                    await asyncio.sleep(
                        min(_MAX_BACKOFF_SECS, _MIN_BACKOFF_SECS * (2 ** bad_retries))
                    )
                    bad_retries += 1

        except asyncio.CancelledError:
            return

    async def _loop_connection(self, connection: Connection[Request, Response]):
        read_task: Awaitable[Response] = asyncio.ensure_future(connection.read())
        write_task: Awaitable[WorkItem[Request]] = asyncio.ensure_future(
            self._write_queue.get()
        )
        while True:
            done, _ = await asyncio.wait(
                [write_task, read_task], return_when=asyncio.FIRST_COMPLETED
            )
            if write_task in done:
                await self._handle_write(connection, await write_task)
                write_task = asyncio.ensure_future(self._write_queue.get())
            if read_task in done:
                await self._read_queue.put(await read_task)
                read_task = asyncio.ensure_future(connection.read())

    @staticmethod
    async def _handle_write(
        connection: Connection[Request, Response], to_write: WorkItem[Request, Response]
    ):
        try:
            await connection.write(to_write.request)
            to_write.response_future.set_result(None)
        except GoogleAPICallError as e:
            to_write.response_future.set_exception(e)
            raise e
