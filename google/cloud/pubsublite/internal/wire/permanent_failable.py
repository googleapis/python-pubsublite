import asyncio
from typing import Awaitable, TypeVar, Optional

from google.api_core.exceptions import GoogleAPICallError

T = TypeVar('T')


class PermanentFailable:
  """A class that can experience permanent failures, with helpers for forwarding these to client actions."""
  _failure_task: asyncio.Future

  def __init__(self):
    self._failure_task = asyncio.Future()

  async def await_unless_failed(self, awaitable: Awaitable[T]) -> T:
    """
    Await the awaitable, unless fail() is called first.
    Args:
      awaitable: An awaitable

    Returns: The result of the awaitable
    Raises: The permanent error if fail() is called or the awaitable raises one.
    """
    if self._failure_task.done():
      raise self._failure_task.exception()
    task = asyncio.ensure_future(awaitable)
    done, _ = await asyncio.wait([task, self._failure_task], return_when=asyncio.FIRST_COMPLETED)
    if task in done:
      return await task
    task.cancel()
    raise self._failure_task.exception()

  def fail(self, err: GoogleAPICallError):
    if not self._failure_task.done():
      self._failure_task.set_exception(err)

  def error(self) -> Optional[GoogleAPICallError]:
    if not self._failure_task.done():
      return None
    return self._failure_task.exception()
