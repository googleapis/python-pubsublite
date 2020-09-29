from abc import abstractmethod
from typing import AsyncContextManager

from google.cloud.pubsublite_v1 import Cursor


class Committer(AsyncContextManager):
    """
  A Committer is able to commit subscribers' completed offsets.
  """

    @abstractmethod
    async def commit(self, cursor: Cursor) -> None:
        pass
