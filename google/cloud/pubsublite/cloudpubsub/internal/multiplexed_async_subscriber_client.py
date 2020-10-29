from typing import (
    Union,
    AsyncIterator,
    Awaitable,
    Callable,
    Optional,
    Set,
)

from google.cloud.pubsub_v1.subscriber.message import Message

from google.cloud.pubsublite.cloudpubsub.internal.client_multiplexer import (
    AsyncClientMultiplexer,
)
from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSubscriberFactory,
    AsyncSingleSubscriber,
)
from google.cloud.pubsublite.cloudpubsub.subscriber_client_interface import (
    AsyncSubscriberClientInterface,
)
from google.cloud.pubsublite.types import (
    SubscriptionPath,
    FlowControlSettings,
    Partition,
)
from overrides import overrides


class _SubscriberAsyncIterator(AsyncIterator):
    _subscriber: AsyncSingleSubscriber
    _on_failure: Callable[[], Awaitable[None]]

    def __init__(
        self,
        subscriber: AsyncSingleSubscriber,
        on_failure: Callable[[], Awaitable[None]],
    ):
        self._subscriber = subscriber
        self._on_failure = on_failure

    async def __anext__(self) -> Message:
        try:
            return await self._subscriber.read()
        except:  # noqa: E722
            await self._on_failure()
            raise

    def __aiter__(self):
        return self


class MultiplexedAsyncSubscriberClient(AsyncSubscriberClientInterface):
    _underlying_factory: AsyncSubscriberFactory
    _multiplexer: AsyncClientMultiplexer[SubscriptionPath, AsyncSingleSubscriber]

    def __init__(self, underlying_factory: AsyncSubscriberFactory):
        self._underlying_factory = underlying_factory
        self._multiplexer = AsyncClientMultiplexer()

    @overrides
    async def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        per_partition_flow_control_settings: FlowControlSettings,
        fixed_partitions: Optional[Set[Partition]] = None,
    ) -> AsyncIterator[Message]:
        if isinstance(subscription, str):
            subscription = SubscriptionPath.parse(subscription)

        async def create_and_open():
            client = self._underlying_factory(
                subscription, fixed_partitions, per_partition_flow_control_settings
            )
            await client.__aenter__()
            return client

        subscriber = await self._multiplexer.get_or_create(
            subscription, create_and_open
        )
        return _SubscriberAsyncIterator(
            subscriber, lambda: self._multiplexer.try_erase(subscription, subscriber)
        )

    @overrides
    async def __aenter__(self):
        await self._multiplexer.__aenter__()
        return self

    @overrides
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._multiplexer.__aexit__(exc_type, exc_value, traceback)
