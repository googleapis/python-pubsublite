from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional, Union, Set, AsyncIterator

from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials
from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
from google.cloud.pubsub_v1.subscriber.message import Message
from google.oauth2 import service_account

from google.cloud.pubsublite.cloudpubsub.internal.make_subscriber import (
    make_async_subscriber,
)
from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_async_subscriber_client import (
    MultiplexedAsyncSubscriberClient,
)
from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_subscriber_client import (
    MultiplexedSubscriberClient,
)
from google.cloud.pubsublite.cloudpubsub.message_transformer import MessageTransformer
from google.cloud.pubsublite.cloudpubsub.nack_handler import NackHandler
from google.cloud.pubsublite.cloudpubsub.subscriber_client_interface import (
    SubscriberClientInterface,
    MessageCallback,
    AsyncSubscriberClientInterface,
)
from google.cloud.pubsublite.types import (
    FlowControlSettings,
    Partition,
    SubscriptionPath,
)


class SubscriberClient(SubscriberClientInterface):
    _impl: SubscriberClientInterface

    def __init__(
        self,
        executor: Optional[ThreadPoolExecutor] = None,
        nack_handler: Optional[NackHandler] = None,
        message_transformer: Optional[MessageTransformer] = None,
        fixed_partitions: Optional[Set[Partition]] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
    ):
        if executor is None:
            executor = ThreadPoolExecutor()
        self._impl = MultiplexedSubscriberClient(
            executor,
            lambda subscription, settings: make_async_subscriber(
                subscription=subscription,
                transport=transport,
                per_partition_flow_control_settings=settings,
                nack_handler=nack_handler,
                message_transformer=message_transformer,
                fixed_partitions=fixed_partitions,
                credentials=credentials,
                client_options=client_options,
            ),
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

    def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        callback: MessageCallback,
        per_partition_flow_control_settings: FlowControlSettings,
    ) -> StreamingPullFuture:
        return self._impl.subscribe(
            subscription, callback, per_partition_flow_control_settings
        )

    def __enter__(self):
        self._impl.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._impl.__exit__(exc_type, exc_value, traceback)


class AsyncSubscriberClient(AsyncSubscriberClientInterface):
    _impl: AsyncSubscriberClientInterface

    def __init__(
        self,
        nack_handler: Optional[NackHandler] = None,
        message_transformer: Optional[MessageTransformer] = None,
        fixed_partitions: Optional[Set[Partition]] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
    ):
        self._impl = MultiplexedAsyncSubscriberClient(
            lambda subscription, settings: make_async_subscriber(
                subscription=subscription,
                transport=transport,
                per_partition_flow_control_settings=settings,
                nack_handler=nack_handler,
                message_transformer=message_transformer,
                fixed_partitions=fixed_partitions,
                credentials=credentials,
                client_options=client_options,
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

    async def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        per_partition_flow_control_settings: FlowControlSettings,
    ) -> AsyncIterator[Message]:
        return await self._impl.subscribe(
            subscription, per_partition_flow_control_settings
        )

    async def __aenter__(self):
        await self._impl.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._impl.__aexit__(exc_type, exc_value, traceback)
