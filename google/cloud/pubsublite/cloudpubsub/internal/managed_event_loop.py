from asyncio import AbstractEventLoop, new_event_loop, run_coroutine_threadsafe
from concurrent.futures import Future
from threading import Thread
from typing import ContextManager


class ManagedEventLoop(ContextManager):
  _loop: AbstractEventLoop
  _thread: Thread

  def __init__(self):
    self._loop = new_event_loop()
    self._thread = Thread(target=lambda: self._loop.run_forever())

  def __enter__(self):
    self._thread.start()

  def __exit__(self, exc_type, exc_value, traceback):
    self._loop.call_soon_threadsafe(self._loop.stop)
    self._thread.join()

  def submit(self, coro) -> Future:
    return run_coroutine_threadsafe(coro, self._loop)
