from typing import Mapping

from google.cloud.pubsublite.internal.wire.publisher import Publisher
from google.cloud.pubsublite.internal.wire.routing_policy import RoutingPolicy
from google.cloud.pubsublite.partition import Partition
from google.cloud.pubsublite.publish_metadata import PublishMetadata
from google.cloud.pubsublite_v1 import PubSubMessage


class RoutingPublisher(Publisher):
  _routing_policy: RoutingPolicy
  _publishers: Mapping[Partition, Publisher]

  def __init__(self, routing_policy: RoutingPolicy, publishers: Mapping[Partition, Publisher]):
    self._routing_policy = routing_policy
    self._publishers = publishers

  async def __aenter__(self):
    for publisher in self._publishers.values():
      await publisher.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    for publisher in self._publishers.values():
      await publisher.__aexit__(exc_type, exc_val, exc_tb)

  async def publish(self, message: PubSubMessage) -> PublishMetadata:
    partition = self._routing_policy.route(message)
    assert partition in self._publishers
    return await self._publishers[partition].publish(message)
