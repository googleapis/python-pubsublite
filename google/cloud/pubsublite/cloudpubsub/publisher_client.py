from concurrent.futures import Future
from typing import Optional, Mapping, Union

from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials
from google.cloud.pubsub_v1.types import BatchSettings

from google.cloud.pubsublite.cloudpubsub.internal.make_publisher import (
    make_publisher,
    make_async_publisher,
)
from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_async_publisher_client import (
    MultiplexedAsyncPublisherClient,
)
from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_publisher_client import (
    MultiplexedPublisherClient,
)
from google.cloud.pubsublite.cloudpubsub.publisher_client_interface import (
    PublisherClientInterface,
    AsyncPublisherClientInterface,
)
from google.cloud.pubsublite.internal.constructable_from_service_account import (
    ConstructableFromServiceAccount,
)
from google.cloud.pubsublite.internal.wire.make_publisher import (
    DEFAULT_BATCHING_SETTINGS as WIRE_DEFAULT_BATCHING,
)
from google.cloud.pubsublite.types import TopicPath
from overrides import overrides


class PublisherClient(PublisherClientInterface, ConstructableFromServiceAccount):
    """
    A PublisherClient publishes messages similar to Google Pub/Sub.
    Any publish failures are unlikely to succeed if retried.

    Must be used in a `with` block or have __enter__() called before use.
    """

    _impl: PublisherClientInterface

    DEFAULT_BATCHING_SETTINGS = WIRE_DEFAULT_BATCHING
    """
    The default batching settings for a publisher client.
    """

    def __init__(
        self,
        per_partition_batching_settings: Optional[BatchSettings] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
    ):
        """
        Create a new PublisherClient.

        Args:
            per_partition_batching_settings: The settings for publish batching. Apply on a per-partition basis.
            credentials: If provided, the credentials to use when connecting.
            transport: The transport to use. Must correspond to an asyncio transport.
            client_options: The client options to use when connecting. If used, must explicitly set `api_endpoint`.
        """
        self._impl = MultiplexedPublisherClient(
            lambda topic: make_publisher(
                topic=topic,
                per_partition_batching_settings=per_partition_batching_settings,
                credentials=credentials,
                client_options=client_options,
                transport=transport,
            )
        )

    def publish(
        self,
        topic: Union[TopicPath, str],
        data: bytes,
        ordering_key: str = "",
        **attrs: Mapping[str, str]
    ) -> "Future[str]":
        return self._impl.publish(
            topic=topic, data=data, ordering_key=ordering_key, **attrs
        )

    def __enter__(self):
        self._impl.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._impl.__exit__(exc_type, exc_value, traceback)


class AsyncPublisherClient(
    AsyncPublisherClientInterface, ConstructableFromServiceAccount
):
    """
    An AsyncPublisherClient publishes messages similar to Google Pub/Sub, but must be used in an
    async context. Any publish failures are unlikely to succeed if retried.

    Must be used in an `async with` block or have __aenter__() awaited before use.
    """

    _impl: AsyncPublisherClientInterface

    DEFAULT_BATCHING_SETTINGS = WIRE_DEFAULT_BATCHING
    """
    The default batching settings for a publisher client.
    """

    def __init__(
        self,
        per_partition_batching_settings: Optional[BatchSettings] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
    ):
        """
        Create a new AsyncPublisherClient.

        Args:
            per_partition_batching_settings: The settings for publish batching. Apply on a per-partition basis.
            credentials: If provided, the credentials to use when connecting.
            transport: The transport to use. Must correspond to an asyncio transport.
            client_options: The client options to use when connecting. If used, must explicitly set `api_endpoint`.
        """
        self._impl = MultiplexedAsyncPublisherClient(
            lambda topic: make_async_publisher(
                topic=topic,
                per_partition_batching_settings=per_partition_batching_settings,
                credentials=credentials,
                client_options=client_options,
                transport=transport,
            )
        )

    @overrides
    async def publish(
        self,
        topic: Union[TopicPath, str],
        data: bytes,
        ordering_key: str = "",
        **attrs: Mapping[str, str]
    ) -> str:
        return await self._impl.publish(
            topic=topic, data=data, ordering_key=ordering_key, **attrs
        )

    @overrides
    async def __aenter__(self):
        await self._impl.__aenter__()
        return self

    @overrides
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._impl.__aexit__(exc_type, exc_value, traceback)
