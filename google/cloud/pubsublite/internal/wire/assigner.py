from abc import abstractmethod
from typing import AsyncContextManager, Set

from google.cloud.pubsublite.partition import Partition


class Assigner(AsyncContextManager):
  """
  An assigner will deliver a continuous stream of assignments when called into. Perform all necessary work with the
  assignment before attempting to get the next one.
  """

  @abstractmethod
  async def get_assignment(self) -> Set[Partition]:
    raise NotImplementedError()
