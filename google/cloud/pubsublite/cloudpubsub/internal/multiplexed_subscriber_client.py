from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock
from typing import Union, Dict

from google.api_core.exceptions import FailedPrecondition
from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture

from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSubscriberFactory,
)
from google.cloud.pubsublite.cloudpubsub.internal.subscriber_impl import SubscriberImpl
from google.cloud.pubsublite.cloudpubsub.subscriber_client_interface import (
    SubscriberClientInterface,
    MessageCallback,
)
from google.cloud.pubsublite.types import SubscriptionPath, FlowControlSettings


class MultiplexedSubscriberClient(SubscriberClientInterface):
    _executor: ThreadPoolExecutor
    _underlying_factory: AsyncSubscriberFactory

    _lock: Lock
    _live_subscribers: Dict[SubscriptionPath, StreamingPullFuture]

    def __init__(
        self, executor: ThreadPoolExecutor, underlying_factory: AsyncSubscriberFactory
    ):
        self._executor = executor
        self._underlying_factory = underlying_factory
        self._lock = Lock()
        self._live_subscribers = {}

    def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        callback: MessageCallback,
        per_partition_flow_control_settings: FlowControlSettings,
    ) -> StreamingPullFuture:
        if isinstance(subscription, str):
            subscription = SubscriptionPath.parse(subscription)
        future: StreamingPullFuture
        with self._lock:
            if subscription in self._live_subscribers:
                raise FailedPrecondition(
                    f"Cannot subscribe to the same subscription twice. {subscription}"
                )
            underlying = self._underlying_factory(
                subscription, per_partition_flow_control_settings
            )
            subscriber = SubscriberImpl(underlying, callback, self._executor)
            future = StreamingPullFuture(subscriber)
            subscriber.__enter__()
            self._live_subscribers[subscription] = future
        future.add_done_callback(lambda fut: self._on_future_failure(subscription, fut))
        return future

    def _on_future_failure(
        self, subscription: SubscriptionPath, future: StreamingPullFuture
    ):
        with self._lock:
            if subscription not in self._live_subscribers:
                return
            current_future = self._live_subscribers[subscription]
            if current_future is not future:
                return
            del self._live_subscribers[subscription]

    def __enter__(self):
        self._executor.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        futures: Dict[SubscriptionPath, StreamingPullFuture]
        with self._lock:
            futures = self._live_subscribers
            self._live_subscribers = {}
        for sub, future in futures.items():
            future.cancel()
            try:
                future.result()
            except:  # noqa: E722
                pass
        self._executor.__exit__(exc_type, exc_value, traceback)
        return super().__exit__(exc_type, exc_value, traceback)
