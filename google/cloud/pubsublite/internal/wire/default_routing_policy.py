import hashlib
import random

from google.cloud.pubsublite.internal.wire.routing_policy import RoutingPolicy
from google.cloud.pubsublite.types import Partition
from google.cloud.pubsublite_v1.types import PubSubMessage


class DefaultRoutingPolicy(RoutingPolicy):
    """
  The default routing policy which routes based on sha256 % num_partitions using the key if set or round robin if
  unset.
  """

    _num_partitions: int
    _current_round_robin: Partition

    def __init__(self, num_partitions: int):
        self._num_partitions = num_partitions
        self._current_round_robin = Partition(random.randint(0, num_partitions - 1))

    def route(self, message: PubSubMessage) -> Partition:
        """Route the message using the key if set or round robin if unset."""
        if not message.key:
            result = Partition(self._current_round_robin.value)
            self._current_round_robin = Partition(
                (self._current_round_robin.value + 1) % self._num_partitions
            )
            return result
        sha = hashlib.sha256()
        sha.update(message.key)
        as_int = int.from_bytes(sha.digest(), byteorder="big")
        return Partition(as_int % self._num_partitions)
