from typing import Callable, Union, Mapping

from google.api_core.exceptions import GoogleAPICallError

from google.cloud.pubsublite.cloudpubsub.internal.client_multiplexer import (
    AsyncClientMultiplexer,
)
from google.cloud.pubsublite.cloudpubsub.internal.single_publisher import (
    AsyncSinglePublisher,
)
from google.cloud.pubsublite.cloudpubsub.publisher_client_interface import (
    AsyncPublisherClientInterface,
)
from google.cloud.pubsublite.types import TopicPath
from overrides import overrides


AsyncPublisherFactory = Callable[[TopicPath], AsyncSinglePublisher]


class MultiplexedAsyncPublisherClient(AsyncPublisherClientInterface):
    _publisher_factory: AsyncPublisherFactory
    _multiplexer: AsyncClientMultiplexer[TopicPath, AsyncSinglePublisher]

    def __init__(self, publisher_factory: AsyncPublisherFactory):
        self._publisher_factory = publisher_factory
        self._multiplexer = AsyncClientMultiplexer()

    @overrides
    async def publish(
        self,
        topic: Union[TopicPath, str],
        data: bytes,
        ordering_key: str = "",
        **attrs: Mapping[str, str]
    ) -> str:
        if isinstance(topic, str):
            topic = TopicPath.parse(topic)

        async def create_and_open():
            client = self._publisher_factory(topic)
            await client.__aenter__()
            return client

        publisher = await self._multiplexer.get_or_create(topic, create_and_open)
        try:
            return await publisher.publish(
                data=data, ordering_key=ordering_key, **attrs
            )
        except GoogleAPICallError as e:
            await self._multiplexer.try_erase(topic, publisher)
            raise e

    @overrides
    async def __aenter__(self):
        await self._multiplexer.__aenter__()
        return self

    @overrides
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._multiplexer.__aexit__(exc_type, exc_value, traceback)
