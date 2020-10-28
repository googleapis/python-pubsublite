from typing import Callable, Dict, Union, Mapping

from google.api_core.exceptions import GoogleAPICallError

from google.cloud.pubsublite.cloudpubsub.internal.single_publisher import (
    AsyncSinglePublisher,
)
from google.cloud.pubsublite.cloudpubsub.publisher_client_interface import (
    AsyncPublisherClientInterface,
)
from google.cloud.pubsublite.types import TopicPath


AsyncPublisherFactory = Callable[[TopicPath], AsyncSinglePublisher]


class MultiplexedAsyncPublisherClient(AsyncPublisherClientInterface):
    _publisher_factory: AsyncPublisherFactory
    _live_publishers: Dict[TopicPath, AsyncSinglePublisher]

    def __init__(self, publisher_factory: AsyncPublisherFactory):
        self._publisher_factory = publisher_factory
        self._live_publishers = {}

    async def publish(
        self,
        topic: Union[TopicPath, str],
        data: bytes,
        ordering_key: str = "",
        **attrs: Mapping[str, str]
    ) -> str:
        if isinstance(topic, str):
            topic = TopicPath.parse(topic)
        publisher: AsyncSinglePublisher
        if topic not in self._live_publishers:
            publisher = self._publisher_factory(topic)
            self._live_publishers[topic] = publisher
            await publisher.__aenter__()
        publisher = self._live_publishers[topic]
        try:
            return await publisher.publish(
                data=data, ordering_key=ordering_key, **attrs
            )
        except GoogleAPICallError as e:
            await self._on_failure(topic, publisher)
            raise e

    async def _on_failure(self, topic: TopicPath, publisher: AsyncSinglePublisher):
        if topic not in self._live_publishers:
            return
        current_publisher = self._live_publishers[topic]
        if current_publisher is not publisher:
            return
        del self._live_publishers[topic]

        await publisher.__aexit__(None, None, None)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        live_publishers = self._live_publishers
        self._live_publishers = {}
        for topic, pub in live_publishers.items():
            await pub.__aexit__(exc_type, exc_value, traceback)
