from typing import AsyncIterator, TypeVar, Optional, Callable, AsyncIterable
import asyncio

from google.cloud.pubsublite.internal.wire.connection import Connection, Request, Response, ConnectionFactory
from google.cloud.pubsublite.internal.wire.work_item import WorkItem
from google.cloud.pubsublite.internal.wire.permanent_failable import PermanentFailable

T = TypeVar('T')


class GapicConnection(Connection[Request, Response], AsyncIterator[Request], PermanentFailable):
  """A Connection wrapping a gapic AsyncIterator[Request/Response] pair."""
  _write_queue: 'asyncio.Queue[WorkItem[Request]]'
  _response_it: Optional[AsyncIterator[Response]]

  def __init__(self):
    super().__init__()
    self._write_queue = asyncio.Queue(maxsize=1)

  def set_response_it(self, response_it: AsyncIterator[Response]):
    self._response_it = response_it

  async def write(self, request: Request) -> None:
    item = WorkItem(request)
    await self.await_or_fail(self._write_queue.put(item))
    await self.await_or_fail(item.response_future)

  async def read(self) -> Response:
    return await self.await_or_fail(self._response_it.__anext__())

  def __aenter__(self):
    return self

  def __aexit__(self, exc_type, exc_value, traceback) -> None:
    pass

  async def __anext__(self) -> Request:
    item: WorkItem[Request] = await self.await_or_fail(self._write_queue.get())
    item.response_future.set_result(None)
    return item.request

  def __aiter__(self) -> AsyncIterator[Response]:
    return self


class GapicConnectionFactory(ConnectionFactory[Request, Response]):
  """A ConnectionFactory that produces GapicConnections."""
  _producer = Callable[[AsyncIterator[Request]], AsyncIterable[Response]]

  def New(self) -> Connection[Request, Response]:
    conn = GapicConnection[Request, Response]()
    response_iterable = self._producer(conn)
    conn.set_response_it(response_iterable.__aiter__())
    return conn
