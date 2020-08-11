from typing import AsyncIterator, Mapping, Optional, MutableMapping

from google.cloud.pubsublite.endpoints import regional_endpoint
from google.cloud.pubsublite.internal.wire.default_routing_policy import DefaultRoutingPolicy
from google.cloud.pubsublite.internal.wire.gapic_connection import GapicConnectionFactory
from google.cloud.pubsublite.internal.wire.merge_metadata import merge_metadata
from google.cloud.pubsublite.internal.wire.publisher import Publisher
from google.cloud.pubsublite.internal.wire.routing_publisher import RoutingPublisher
from google.cloud.pubsublite.internal.wire.single_partition_publisher import SinglePartitionPublisher
from google.cloud.pubsublite.partition import Partition
from google.cloud.pubsublite.paths import TopicPath
from google.cloud.pubsublite.routing_metadata import topic_routing_metadata
from google.cloud.pubsublite_v1 import InitialPublishRequest, PublishRequest
from google.cloud.pubsublite_v1.services.publisher_service import async_client
from google.cloud.pubsublite_v1.services.admin_service.client import AdminServiceClient
from google.cloud.pubsublite_v1.types.admin import GetTopicPartitionsRequest
from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials


def make_publisher(
    topic: TopicPath,
    batching_delay_secs: float = .05,
    credentials: Optional[Credentials] = None,
    client_options: Optional[ClientOptions] = None,
    metadata: Optional[Mapping[str, str]] = None) -> Publisher:
  if client_options is None:
    client_options = ClientOptions(api_endpoint=regional_endpoint(topic.location.region))
  client = async_client.PublisherServiceAsyncClient(
    credentials=credentials, client_options=client_options)  # type: ignore

  admin_client = AdminServiceClient(credentials=credentials, client_options=client_options)
  partitions = admin_client.get_topic_partitions(GetTopicPartitionsRequest(name=str(topic)))

  clients: MutableMapping[Partition, Publisher] = {}

  for partition in range(partitions.partition_count):
    partition = Partition(partition)

    def connection_factory(requests: AsyncIterator[PublishRequest]):
      final_metadata = merge_metadata(metadata, topic_routing_metadata(topic, partition))
      return client.publish(requests, metadata=list(final_metadata.items()))

    clients[partition] = SinglePartitionPublisher(InitialPublishRequest(topic=str(topic), partition=partition.value),
                                                  batching_delay_secs, GapicConnectionFactory(connection_factory))
  return RoutingPublisher(DefaultRoutingPolicy(partitions.partition_count), clients)
