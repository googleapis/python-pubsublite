from typing import Optional, Union, Mapping

from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials
from google.cloud.pubsub_v1.types import BatchSettings
from google.oauth2 import service_account

from google.cloud.pubsublite.cloudpubsub.internal.async_publisher_impl import (
    AsyncPublisherImpl,
)
from google.cloud.pubsublite.cloudpubsub.internal.publisher_impl import PublisherImpl
from google.cloud.pubsublite.cloudpubsub.make_publisher import make_async_publisher
from google.cloud.pubsublite.cloudpubsub.publisher import AsyncPublisher, Publisher
from google.cloud.pubsublite.internal.wire.make_publisher import (
    make_publisher as make_wire_publisher,
    DEFAULT_BATCHING_SETTINGS as WIRE_DEFAULT_BATCHING,
)
from google.cloud.pubsublite.internal.wire.merge_metadata import merge_metadata
from google.cloud.pubsublite.internal.wire.pubsub_context import pubsub_context
from google.cloud.pubsublite.types import TopicPath

from google.cloud.pubsublite_v1.services.subscriber_service.transports import (
    SubscriberServiceTransport,
)


class PublisherClient:
    _credentials: Optional[Credentials]
    _transport: Union[str, SubscriberServiceTransport]
    _client_options: Optional[ClientOptions]

    DEFAULT_BATCHING_SETTINGS = WIRE_DEFAULT_BATCHING

    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        transport: Union[str, SubscriberServiceTransport] = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
    ):
        self._credentials = credentials
        self._transport = transport
        self._client_options = client_options

    @classmethod
    def from_service_account_file(cls, filename, **kwargs):
        """Creates an instance of this client using the provided credentials
        file.
        Args:
            filename (str): The path to the service account private key json
                file.
            kwargs: Additional arguments to pass to the constructor.
        Returns:
            A PublisherClient.
        """
        credentials = service_account.Credentials.from_service_account_file(filename)
        return cls(credentials=credentials, **kwargs)

    from_service_account_json = from_service_account_file

    def make_async_publisher(
        self,
        topic: TopicPath,
        per_partition_batching_settings: Optional[BatchSettings] = None,
        metadata: Optional[Mapping[str, str]] = None,
    ) -> AsyncPublisher:
        """
      Make a new publisher for the given topic.

      Args:
        topic: The topic to publish to.
        per_partition_batching_settings: Settings for batching messages on each partition. The default is reasonable for most cases.
        metadata: Additional metadata to send with the RPC.

      Returns:
        A new AsyncPublisher.

      Throws:
        GoogleApiCallException on any error determining topic structure.
      """
        metadata = merge_metadata(
            pubsub_context(framework="CLOUD_PUBSUB_SHIM"), metadata
        )

        def underlying_factory():
            return make_wire_publisher(
                topic,
                per_partition_batching_settings,
                self._credentials,
                self._client_options,
                metadata,
            )

        return AsyncPublisherImpl(underlying_factory)

    def make_publisher(
        self,
        topic: TopicPath,
        per_partition_batching_settings: Optional[BatchSettings] = None,
        metadata: Optional[Mapping[str, str]] = None,
    ) -> Publisher:
        """
      Make a new publisher for the given topic.

      Args:
        topic: The topic to publish to.
        per_partition_batching_settings: Settings for batching messages on each partition. The default is reasonable for most cases.
        metadata: Additional metadata to send with the RPC.

      Returns:
        A new Publisher.

      Throws:
        GoogleApiCallException on any error determining topic structure.
      """
        return PublisherImpl(
            make_async_publisher(topic, per_partition_batching_settings, metadata,)
        )
