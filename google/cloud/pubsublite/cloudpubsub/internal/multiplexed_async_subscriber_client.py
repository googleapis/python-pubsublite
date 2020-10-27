from typing import (
    Union,
    AsyncIterator,
    Awaitable,
    Dict,
    Callable,
)

from google.api_core.exceptions import FailedPrecondition
from google.cloud.pubsub_v1.subscriber.message import Message

from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSubscriberFactory,
    AsyncSingleSubscriber,
)
from google.cloud.pubsublite.cloudpubsub.subscriber_client_interface import (
    AsyncSubscriberClientInterface,
)
from google.cloud.pubsublite.types import SubscriptionPath, FlowControlSettings


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
    _live_subscribers: Dict[SubscriptionPath, AsyncSingleSubscriber]

    def __init__(self, underlying_factory: AsyncSubscriberFactory):
        self._underlying_factory = underlying_factory
        self._live_subscribers = {}

    async def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        per_partition_flow_control_settings: FlowControlSettings,
    ) -> AsyncIterator[Message]:
        if isinstance(subscription, str):
            subscription = SubscriptionPath.parse(subscription)
        if subscription in self._live_subscribers:
            raise FailedPrecondition(
                f"Cannot subscribe to the same subscription twice. {subscription}"
            )
        subscriber = self._underlying_factory(
            subscription, per_partition_flow_control_settings
        )
        self._live_subscribers[subscription] = subscriber
        await subscriber.__aenter__()
        return _SubscriberAsyncIterator(
            subscriber, lambda: self._on_subscriber_failure(subscription, subscriber)
        )

    async def _on_subscriber_failure(
        self, subscription: SubscriptionPath, subscriber: AsyncSingleSubscriber
    ):
        if subscription not in self._live_subscribers:
            return
        current_subscriber = self._live_subscribers[subscription]
        if current_subscriber is not subscriber:
            return
        del self._live_subscribers[subscription]
        await subscriber.__aexit__(None, None, None)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        live_subscribers = self._live_subscribers
        self._live_subscribers = {}
        for topic, sub in live_subscribers.items():
            await sub.__aexit__(exc_type, exc_value, traceback)
