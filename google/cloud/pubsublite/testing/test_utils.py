import asyncio
from typing import List, Union, Any, TypeVar, Generic, Optional

from asynctest import CoroutineMock

T = TypeVar("T")


async def async_iterable(elts: List[Union[Any, Exception]]):
    for elt in elts:
        if isinstance(elt, Exception):
            raise elt
        yield elt


def make_queue_waiter(
    started_q: "asyncio.Queue[None]", result_q: "asyncio.Queue[Union[T, Exception]]"
):
    """
  Given a queue to notify when started and a queue to get results from, return a waiter which
  notifies started_q when started and returns from result_q when done.
  """

    async def waiter(*args, **kwargs):
        await started_q.put(None)
        result = await result_q.get()
        if isinstance(result, Exception):
            raise result
        return result

    return waiter


class QueuePair:
    called: asyncio.Queue
    results: asyncio.Queue

    def __init__(self):
        self.called = asyncio.Queue()
        self.results = asyncio.Queue()


def wire_queues(mock: CoroutineMock) -> QueuePair:
    queues = QueuePair()
    mock.side_effect = make_queue_waiter(queues.called, queues.results)
    return queues


class Box(Generic[T]):
    val: Optional[T]
