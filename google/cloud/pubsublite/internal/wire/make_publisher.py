from typing import AsyncIterator, Mapping, Optional, MutableMapping

from google.cloud.pubsub_v1.types import BatchSettings

from google.cloud.pubsublite.make_admin_client import make_admin_client
from google.cloud.pubsublite.internal.endpoints import regional_endpoint
from google.cloud.pubsublite.internal.wire.default_routing_policy import (
    DefaultRoutingPolicy,
)
from google.cloud.pubsublite.internal.wire.gapic_connection import (
    GapicConnectionFactory,
)
from google.cloud.pubsublite.internal.wire.merge_metadata import merge_metadata
from google.cloud.pubsublite.internal.wire.publisher import Publisher
from google.cloud.pubsublite.internal.wire.routing_publisher import RoutingPublisher
from google.cloud.pubsublite.internal.wire.single_partition_publisher import (
    SinglePartitionPublisher,
)
from google.cloud.pubsublite.types import Partition, TopicPath
from google.cloud.pubsublite.internal.routing_metadata import topic_routing_metadata
from google.cloud.pubsublite_v1 import InitialPublishRequest, PublishRequest
from google.cloud.pubsublite_v1.services.publisher_service import async_client
from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials

DEFAULT_BATCHING_SETTINGS = BatchSettings(
    max_bytes=(
        3 * 1024 * 1024
    ),  # 3 MiB to stay 1 MiB below GRPC's 4 MiB per-message limit.
    max_messages=1000,
    max_latency=0.05,  # 50 ms
)


def make_publisher(
    topic: TopicPath,
    transport: str,
    per_partition_batching_settings: Optional[BatchSettings] = None,
    credentials: Optional[Credentials] = None,
    client_options: Optional[ClientOptions] = None,
    metadata: Optional[Mapping[str, str]] = None,
) -> Publisher:
    """
  Make a new publisher for the given topic.

  Args:
    topic: The topic to publish to.
    transport: The transport type to use.
    per_partition_batching_settings: Settings for batching messages on each partition. The default is reasonable for most cases.
    credentials: The credentials to use to connect. GOOGLE_DEFAULT_CREDENTIALS is used if None.
    client_options: Other options to pass to the client. Note that if you pass any you must set api_endpoint.
    metadata: Additional metadata to send with the RPC.

  Returns:
    A new Publisher.

  Throws:
    GoogleApiCallException on any error determining topic structure.
  """
    if per_partition_batching_settings is None:
        per_partition_batching_settings = DEFAULT_BATCHING_SETTINGS
    admin_client = make_admin_client(
        region=topic.location.region,
        transport=transport,
        credentials=credentials,
        client_options=client_options,
    )
    if client_options is None:
        client_options = ClientOptions(
            api_endpoint=regional_endpoint(topic.location.region)
        )
    client = async_client.PublisherServiceAsyncClient(
        credentials=credentials, transport=transport, client_options=client_options
    )  # type: ignore

    clients: MutableMapping[Partition, Publisher] = {}

    partition_count = admin_client.get_topic_partition_count(topic)
    for partition in range(partition_count):
        partition = Partition(partition)

        def connection_factory(requests: AsyncIterator[PublishRequest]):
            final_metadata = merge_metadata(
                metadata, topic_routing_metadata(topic, partition)
            )
            return client.publish(requests, metadata=list(final_metadata.items()))

        clients[partition] = SinglePartitionPublisher(
            InitialPublishRequest(topic=str(topic), partition=partition.value),
            per_partition_batching_settings,
            GapicConnectionFactory(connection_factory),
        )
    return RoutingPublisher(DefaultRoutingPolicy(partition_count), clients)
