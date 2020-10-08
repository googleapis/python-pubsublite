from typing import Mapping, Callable, Optional

from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub.message_transforms import (
    from_cps_publish_message,
)
from google.cloud.pubsublite.cloudpubsub.publisher import AsyncPublisher
from google.cloud.pubsublite.internal.wire.publisher import Publisher


class AsyncPublisherImpl(AsyncPublisher):
    _publisher_factory: Callable[[], Publisher]
    _publisher: Optional[Publisher]

    def __init__(self, publisher_factory: Callable[[], Publisher]):
        """
        Accepts a factory for a Publisher instead of a Publisher because GRPC asyncio uses the current thread's event
        loop.
        """
        super().__init__()
        self._publisher_factory = publisher_factory
        self._publisher = None

    async def publish(
        self, data: bytes, ordering_key: str = "", **attrs: Mapping[str, str]
    ) -> str:
        cps_message = PubsubMessage(
            data=data, ordering_key=ordering_key, attributes=attrs
        )
        psl_message = from_cps_publish_message(cps_message)
        return (await self._publisher.publish(psl_message)).encode()

    async def __aenter__(self):
        self._publisher = self._publisher_factory()
        await self._publisher.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._publisher.__aexit__(exc_type, exc_value, traceback)
