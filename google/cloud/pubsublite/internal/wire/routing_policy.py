from abc import ABC, abstractmethod

from google.cloud.pubsublite.partition import Partition
from google.cloud.pubsublite_v1.types.common import PubSubMessage


class RoutingPolicy(ABC):
    """A policy for how to route messages."""

    @abstractmethod
    def route(self, message: PubSubMessage) -> Partition:
        """
    Route a message to a given partition.
    Args:
      message: The message to route

    Returns: The partition to route to

    """
        raise NotImplementedError()
