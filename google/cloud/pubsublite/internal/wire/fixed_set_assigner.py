import asyncio
from typing import Set

from google.cloud.pubsublite.internal.wire.assigner import Assigner
from google.cloud.pubsublite.partition import Partition


class FixedSetAssigner(Assigner):
    _partitions: Set[Partition]
    _returned_set: bool

    def __init__(self, partitions: Set[Partition]):
        self._partitions = partitions
        self._returned_set = False

    async def get_assignment(self) -> Set[Partition]:
        """Only returns an assignment the first iteration."""
        if self._returned_set:
            await asyncio.sleep(float("inf"))
            raise RuntimeError("Should never happen.")
        self._returned_set = True
        return self._partitions

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass
