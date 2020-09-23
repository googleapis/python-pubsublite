import concurrent.futures
import threading
from asyncio import CancelledError
from concurrent.futures.thread import ThreadPoolExecutor
from typing import ContextManager, Optional
from google.api_core.exceptions import GoogleAPICallError
from google.cloud.pubsublite.cloudpubsub.internal.managed_event_loop import ManagedEventLoop
from google.cloud.pubsublite.cloudpubsub.internal.streaming_pull_manager import StreamingPullManager, CloseCallback
from google.cloud.pubsublite.cloudpubsub.subscriber import AsyncSubscriber, MessageCallback


class SubscriberImpl(ContextManager, StreamingPullManager):
  _underlying: AsyncSubscriber
  _callback: MessageCallback
  _executor: ThreadPoolExecutor

  _event_loop: ManagedEventLoop

  _poller_future: concurrent.futures.Future
  _close_lock: threading.Lock
  _failure: Optional[GoogleAPICallError]
  _close_callback: Optional[CloseCallback]
  _closed: bool

  def __init__(self, underlying: AsyncSubscriber, callback: MessageCallback, executor: ThreadPoolExecutor):
    self._underlying = underlying
    self._callback = callback
    self._executor = executor
    self._event_loop = ManagedEventLoop()
    self._close_lock = threading.Lock()
    self._failure = None
    self._close_callback = None
    self._closed = False

  def add_close_callback(self, close_callback: CloseCallback):
    with self._close_lock:
      assert self._close_callback is None
      self._close_callback = close_callback

  def close(self):
    with self._close_lock:
      if not self._closed:
        self._closed = True
        self.__exit__(None, None, None)

  def _fail(self, error: GoogleAPICallError):
    self._failure = error
    self.close()

  async def _poller(self):
    try:
      while True:
        message = await self._underlying.read()
        self._executor.submit(self._callback, message)
    except GoogleAPICallError as e:
      self._executor.submit(lambda: self._fail(e))

  def __enter__(self):
    assert self._close_callback is not None
    self._event_loop.__enter__()
    self._event_loop.submit(self._underlying.__aenter__()).result()
    self._poller_future = self._event_loop.submit(self._poller())
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    try:
      self._poller_future.cancel()
      self._poller_future.result()
    except CancelledError:
      pass
    self._event_loop.submit(self._underlying.__aexit__(exc_type, exc_value, traceback)).result()
    self._event_loop.__exit__(exc_type, exc_value, traceback)
    assert self._close_callback is not None
    self._executor.shutdown(wait=False)  # __exit__ may be called from the executor.
    self._close_callback(self, self._failure)
