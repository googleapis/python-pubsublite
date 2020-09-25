from typing import AsyncIterator, Mapping, Optional, MutableMapping

from google.cloud.pubsublite.admin_client import make_admin_client
from google.cloud.pubsublite.endpoints import regional_endpoint
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
from google.cloud.pubsublite.partition import Partition
from google.cloud.pubsublite.paths import TopicPath
from google.cloud.pubsublite.routing_metadata import topic_routing_metadata
from google.cloud.pubsublite_v1 import InitialPublishRequest, PublishRequest
from google.cloud.pubsublite_v1.services.publisher_service import async_client
from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials


def make_publisher(
    topic: TopicPath,
    batching_delay_secs: Optional[float] = None,
    credentials: Optional[Credentials] = None,
    client_options: Optional[ClientOptions] = None,
    metadata: Optional[Mapping[str, str]] = None,
) -> Publisher:
    """
  Make a new publisher for the given topic.

  Args:
    topic: The topic to publish to.
    batching_delay_secs: The delay in seconds to batch messages. The default is reasonable for most cases.
    credentials: The credentials to use to connect. GOOGLE_DEFAULT_CREDENTIALS is used if None.
    client_options: Other options to pass to the client. Note that if you pass any you must set api_endpoint.
    metadata: Additional metadata to send with the RPC.

  Returns:
    A new Publisher.

  Throws:
    GoogleApiCallException on any error determining topic structure.
  """
    batching_delay_secs = (
        batching_delay_secs if batching_delay_secs is not None else 0.05
    )
    admin_client = make_admin_client(
        region=topic.location.region,
        credentials=credentials,
        client_options=client_options,
    )
    if client_options is None:
        client_options = ClientOptions(
            api_endpoint=regional_endpoint(topic.location.region)
        )
    client = async_client.PublisherServiceAsyncClient(
        credentials=credentials, client_options=client_options
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
            batching_delay_secs,
            GapicConnectionFactory(connection_factory),
        )
    return RoutingPublisher(DefaultRoutingPolicy(partition_count), clients)
