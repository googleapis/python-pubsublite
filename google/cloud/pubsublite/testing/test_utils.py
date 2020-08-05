from abc import abstractmethod
from typing import List, Union, Any, Generic
from unittest.mock import Mock

from google.cloud.pubsublite.internal.wire.connection import Connection, Request, Response


async def async_iterable(elts: List[Union[Any, Exception]]):
  for elt in elts:
    if isinstance(elt, Exception):
      raise elt
    yield elt
