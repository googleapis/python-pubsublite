import asyncio
from typing import Awaitable, TypeVar, Optional, Callable

from google.api_core.exceptions import GoogleAPICallError

T = TypeVar("T")


class PermanentFailable:
    """A class that can experience permanent failures, with helpers for forwarding these to client actions."""

    _maybe_failure_task: Optional[asyncio.Future]

    def __init__(self):
        self._maybe_failure_task = None

    @property
    def _failure_task(self) -> asyncio.Future:
        """Get the failure task, initializing it lazily, since it needs to be initialized in the event loop."""
        if self._maybe_failure_task is None:
            self._maybe_failure_task = asyncio.Future()
        return self._maybe_failure_task

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
        done, _ = await asyncio.wait(
            [task, self._failure_task], return_when=asyncio.FIRST_COMPLETED
        )
        if task in done:
            return await task
        task.cancel()
        raise self._failure_task.exception()

    async def run_poller(self, poll_action: Callable[[], Awaitable[None]]):
        """
    Run a polling loop, which runs poll_action forever unless this is failed.
    Args:
      poll_action: A callable returning an awaitable to run in a loop. Note that async functions which return once
      satisfy this.
    """
        try:
            while True:
                await self.await_unless_failed(poll_action())
        except GoogleAPICallError as e:
            self.fail(e)

    def fail(self, err: GoogleAPICallError):
        if not self._failure_task.done():
            self._failure_task.set_exception(err)

    def error(self) -> Optional[GoogleAPICallError]:
        if not self._failure_task.done():
            return None
        return self._failure_task.exception()
