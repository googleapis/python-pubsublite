from typing import Optional, Mapping

from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials
from google.cloud.pubsub_v1.types import BatchSettings

from google.cloud.pubsublite.cloudpubsub.internal.async_publisher_impl import (
    AsyncPublisherImpl,
)
from google.cloud.pubsublite.cloudpubsub.internal.publisher_impl import PublisherImpl
from google.cloud.pubsublite.cloudpubsub.publisher import AsyncPublisher, Publisher
from google.cloud.pubsublite.internal.wire.make_publisher import (
    make_publisher as make_wire_publisher,
    DEFAULT_BATCHING_SETTINGS as WIRE_DEFAULT_BATCHING,
)
from google.cloud.pubsublite.internal.wire.merge_metadata import merge_metadata
from google.cloud.pubsublite.internal.wire.pubsub_context import pubsub_context
from google.cloud.pubsublite.paths import TopicPath


DEFAULT_BATCHING_SETTINGS = WIRE_DEFAULT_BATCHING


def make_async_publisher(
    topic: TopicPath,
    per_partition_batching_settings: Optional[BatchSettings] = None,
    credentials: Optional[Credentials] = None,
    client_options: Optional[ClientOptions] = None,
    metadata: Optional[Mapping[str, str]] = None,
) -> AsyncPublisher:
    """
  Make a new publisher for the given topic.

  Args:
    topic: The topic to publish to.
    per_partition_batching_settings: Settings for batching messages on each partition. The default is reasonable for most cases.
    credentials: The credentials to use to connect. GOOGLE_DEFAULT_CREDENTIALS is used if None.
    client_options: Other options to pass to the client. Note that if you pass any you must set api_endpoint.
    metadata: Additional metadata to send with the RPC.

  Returns:
    A new AsyncPublisher.

  Throws:
    GoogleApiCallException on any error determining topic structure.
  """
    metadata = merge_metadata(pubsub_context(framework="CLOUD_PUBSUB_SHIM"), metadata)

    def underlying_factory():
        return make_wire_publisher(
            topic,
            per_partition_batching_settings,
            credentials,
            client_options,
            metadata,
        )

    return AsyncPublisherImpl(underlying_factory)


def make_publisher(
    topic: TopicPath,
    per_partition_batching_settings: Optional[BatchSettings] = None,
    credentials: Optional[Credentials] = None,
    client_options: Optional[ClientOptions] = None,
    metadata: Optional[Mapping[str, str]] = None,
) -> Publisher:
    """
  Make a new publisher for the given topic.

  Args:
    topic: The topic to publish to.
    per_partition_batching_settings: Settings for batching messages on each partition. The default is reasonable for most cases.
    credentials: The credentials to use to connect. GOOGLE_DEFAULT_CREDENTIALS is used if None.
    client_options: Other options to pass to the client. Note that if you pass any you must set api_endpoint.
    metadata: Additional metadata to send with the RPC.

  Returns:
    A new Publisher.

  Throws:
    GoogleApiCallException on any error determining topic structure.
  """
    return PublisherImpl(
        make_async_publisher(
            topic,
            per_partition_batching_settings,
            credentials,
            client_options,
            metadata,
        )
    )
