from abc import ABCMeta, abstractmethod
from typing import Generic, List, Tuple, Dict
import asyncio

from google.cloud.pubsublite.internal.wire.connection import Request, Response
from google.cloud.pubsublite.internal.wire.work_item import WorkItem


class RequestSender(Generic[Request, Response], metaclass=ABCMeta):
  @abstractmethod
  async def send(self, requests: List[Request]) -> List[Response]:
    """
    Send the requests, and return the responses.

    Throws:
      GoogleAPICallError: On an error.
    """
    raise NotImplementedError()


class Aggregator(Generic[Request, Response]):
  class _AggregatorState:
    gen: int
    items: List[WorkItem[Request]]

    def __init__(self, gen: int):
      self.gen = gen
      self.items = []

  _request_sender: RequestSender[Request, Response]
  _period_secs: float

  _state: _AggregatorState
  _outstanding_states: Dict[_AggregatorState, asyncio.Future]  # A mapping from the AggregatorState to a task.

  _loop_future: asyncio.Future

  def __init__(self, request_sender: RequestSender[Request, Response], period_secs: float):
    self._request_sender = request_sender
    self._period_secs = period_secs
    self._state = self._AggregatorState(gen=0)
    self._outstanding_states = {}

  async def __aenter__(self):
    self._loop_future = asyncio.ensure_future(self._run_loop())
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    self._loop_future.cancel()
    await self._loop_future
    self._send()
    await asyncio.gather(*self._outstanding_states.values())

  async def _run_loop(self) -> None:
    """Run a loop to process futures. When any exception is thrown, aborts."""
    try:
      while True:
        self._send()
        await asyncio.sleep(self._period_secs)
    except asyncio.CancelledError:
      return

  def _next_state(self) -> _AggregatorState:
    state = self._state
    self._state = self._AggregatorState(gen=state.gen + 1)
    return state

  def _send(self):
    if not self._state.items:
      return
    state = self._next_state()
    task = asyncio.ensure_future(self._process(state))  # ensure_future does not run until this yields.
    self._outstanding_states[state] = task

  async def _process(self, state: _AggregatorState):
    responses = await self._request_sender.send([x.request for x in state.items])
    for idx, response in enumerate(responses):
      state.items[idx].response_future.set_result(response)
    del self._outstanding_states[state]

  async def push(self, request: Request) -> Response:
    work = WorkItem(request)
    self._state.items.append(work)
    return await work.response_future

  async def restart(self) -> None:
    """Resends all outstanding requests in order."""
    # Cancel looping
    self._loop_future.cancel()
    # Cancel all outstanding requests
    for fut in self._outstanding_states.values():
      fut.cancel()
    await self._loop_future
    # Handle the existing request
    if self._state.items:
      self._outstanding_states[self._next_state()] = asyncio.Future()
    # Order by generation, increasing
    sorted_states = sorted(self._outstanding_states.keys(), key=lambda s: s.gen)
    # Send all batches in order. _process removes them from _outstanding_states if it completes.
    for state in sorted_states:
      await self._process(state)
    # Restart looping
    self._loop_future = asyncio.ensure_future(self._run_loop())
