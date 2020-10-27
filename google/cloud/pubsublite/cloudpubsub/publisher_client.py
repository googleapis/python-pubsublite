from concurrent.futures import Future
from typing import Optional, Mapping, Union

from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials
from google.cloud.pubsub_v1.types import BatchSettings
from google.oauth2 import service_account

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
from google.cloud.pubsublite.internal.wire.make_publisher import (
    DEFAULT_BATCHING_SETTINGS as WIRE_DEFAULT_BATCHING,
)
from google.cloud.pubsublite.types import TopicPath


class PublisherClient(PublisherClientInterface):
    _impl: PublisherClientInterface

    DEFAULT_BATCHING_SETTINGS = WIRE_DEFAULT_BATCHING

    def __init__(
        self,
        per_partition_batching_setttings: Optional[BatchSettings] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
    ):
        self._impl = MultiplexedPublisherClient(
            lambda topic: make_publisher(
                topic=topic,
                per_partition_batching_settings=per_partition_batching_setttings,
                credentials=credentials,
                client_options=client_options,
                transport=transport,
            )
        )

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


class AsyncPublisherClient(AsyncPublisherClientInterface):
    _impl: AsyncPublisherClientInterface

    DEFAULT_BATCHING_SETTINGS = WIRE_DEFAULT_BATCHING

    def __init__(
        self,
        per_partition_batching_setttings: Optional[BatchSettings] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
    ):
        self._impl = MultiplexedAsyncPublisherClient(
            lambda topic: make_async_publisher(
                topic=topic,
                per_partition_batching_settings=per_partition_batching_setttings,
                credentials=credentials,
                client_options=client_options,
                transport=transport,
            )
        )

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

    async def __aenter__(self):
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._impl.__aexit__(exc_type, exc_value, traceback)
