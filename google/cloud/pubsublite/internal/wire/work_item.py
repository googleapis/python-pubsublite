import asyncio
from typing import Generic, TypeVar

T = TypeVar('T')


class WorkItem(Generic[T]):
  request: T
  response_future: "asyncio.Future[None]"

  def __init__(self, request: T):
    self.request = request
    self.response_future = asyncio.Future()
