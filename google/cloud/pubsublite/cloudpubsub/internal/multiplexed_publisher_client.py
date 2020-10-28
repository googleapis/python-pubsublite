from concurrent.futures import Future
from threading import Lock
from typing import Callable, Dict, Union, Mapping

from google.api_core.exceptions import GoogleAPICallError

from google.cloud.pubsublite.cloudpubsub.internal.single_publisher import (
    SinglePublisher,
)
from google.cloud.pubsublite.cloudpubsub.publisher_client_interface import (
    PublisherClientInterface,
)
from google.cloud.pubsublite.types import TopicPath

PublisherFactory = Callable[[TopicPath], SinglePublisher]


class MultiplexedPublisherClient(PublisherClientInterface):
    _publisher_factory: PublisherFactory

    _lock: Lock
    _live_publishers: Dict[TopicPath, SinglePublisher]

    def __init__(self, publisher_factory: PublisherFactory):
        self._publisher_factory = publisher_factory
        self._lock = Lock()
        self._live_publishers = {}

    def publish(
        self,
        topic: Union[TopicPath, str],
        data: bytes,
        ordering_key: str = "",
        **attrs: Mapping[str, str]
    ) -> "Future[str]":
        if isinstance(topic, str):
            topic = TopicPath.parse(topic)
        publisher: SinglePublisher
        with self._lock:
            if topic not in self._live_publishers:
                publisher = self._publisher_factory(topic)
                publisher.__enter__()
                self._live_publishers[topic] = publisher
            publisher = self._live_publishers[topic]
        future = publisher.publish(data=data, ordering_key=ordering_key, **attrs)
        future.add_done_callback(
            lambda fut: self._on_future_completion(topic, publisher, fut)
        )
        return future

    def _on_future_completion(
        self, topic: TopicPath, publisher: SinglePublisher, future: "Future[str]"
    ):
        try:
            future.result()
        except GoogleAPICallError:
            with self._lock:
                if topic not in self._live_publishers:
                    return
                current_publisher = self._live_publishers[topic]
                if current_publisher is not publisher:
                    return
                del self._live_publishers[topic]
            publisher.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        live_publishers: Dict[TopicPath, SinglePublisher]
        with self._lock:
            live_publishers = self._live_publishers
            self._live_publishers = {}
        for topic, pub in live_publishers.items():
            pub.__exit__(exc_type, exc_value, traceback)
