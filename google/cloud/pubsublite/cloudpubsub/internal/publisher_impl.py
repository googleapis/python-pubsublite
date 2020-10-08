from concurrent.futures import Future
from typing import Mapping

from google.cloud.pubsublite.cloudpubsub.internal.managed_event_loop import (
    ManagedEventLoop,
)
from google.cloud.pubsublite.cloudpubsub.publisher import Publisher, AsyncPublisher


class PublisherImpl(Publisher):
    _managed_loop: ManagedEventLoop
    _underlying: AsyncPublisher

    def __init__(self, underlying: AsyncPublisher):
        super().__init__()
        self._managed_loop = ManagedEventLoop()
        self._underlying = underlying

    def publish(
        self, data: bytes, ordering_key: str = "", **attrs: Mapping[str, str]
    ) -> "Future[str]":
        return self._managed_loop.submit(
            self._underlying.publish(data=data, ordering_key=ordering_key, **attrs)
        )

    def __enter__(self):
        self._managed_loop.__enter__()
        self._managed_loop.submit(self._underlying.__aenter__()).result()
        return self

    def __exit__(self, __exc_type, __exc_value, __traceback):
        self._managed_loop.submit(
            self._underlying.__aexit__(__exc_type, __exc_value, __traceback)
        ).result()
        self._managed_loop.__exit__(__exc_type, __exc_value, __traceback)
