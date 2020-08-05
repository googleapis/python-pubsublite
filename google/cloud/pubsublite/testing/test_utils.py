import asyncio
from abc import abstractmethod
from typing import List, Union, Any, Generic, TypeVar, NamedTuple, Optional
from unittest.mock import Mock

from google.cloud.pubsublite.internal.wire.connection import Connection, Request, Response


async def async_iterable(elts: List[Union[Any, Exception]]):
  for elt in elts:
    if isinstance(elt, Exception):
      raise elt
    yield elt


T = TypeVar("T")


def make_queue_waiter(started_q: "asyncio.Queue[None]", result_q: "asyncio.Queue[Union[T, Exception]]"):
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


class Box(Generic[T]):
  val: Optional[T]
