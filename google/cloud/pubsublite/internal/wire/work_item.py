import asyncio
from typing import Generic

from google.cloud.pubsublite.internal.wire.connection import Request, Response


class WorkItem(Generic[Request, Response]):
  """An item of work and a future to complete when it is finished."""
  request: Request
  response_future: "asyncio.Future[Response]"

  def __init__(self, request: Request):
    self.request = request
    self.response_future = asyncio.Future()
