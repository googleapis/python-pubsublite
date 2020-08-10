import asyncio
from typing import Awaitable, TypeVar, Optional

from google.api_core.exceptions import GoogleAPICallError

T = TypeVar('T')


class PermanentFailable:
  """A class that can experience permanent failures, with helpers for forwarding these to client actions."""
  _failure_task: asyncio.Future

  def __init__(self):
    self._failure_task = asyncio.Future()

  async def await_or_fail(self, awaitable: Awaitable[T]) -> T:
    if self._failure_task.done():
      raise self._failure_task.exception()
    task = asyncio.ensure_future(awaitable)
    done, _ = await asyncio.wait([task, self._failure_task], return_when=asyncio.FIRST_COMPLETED)
    if task in done:
      try:
        return await task
      except GoogleAPICallError as e:
        self.fail(e)
    task.cancel()
    raise self._failure_task.exception()

  def fail(self, err: GoogleAPICallError):
    if not self._failure_task.done():
      self._failure_task.set_exception(err)

  def error(self) -> Optional[GoogleAPICallError]:
    if not self._failure_task.done():
      return None
    return self._failure_task.exception()
