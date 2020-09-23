from typing import Mapping

from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub.message_transforms import from_cps_publish_message
from google.cloud.pubsublite.cloudpubsub.publisher import AsyncPublisher
from google.cloud.pubsublite.internal.wire.publisher import Publisher


class AsyncPublisherImpl(AsyncPublisher):
  _publisher: Publisher

  def __init__(self, publisher: Publisher):
    super().__init__()
    self._publisher = publisher

  async def publish(self, data: bytes, ordering_key: str = "", **attrs: Mapping[str, str]) -> str:
    cps_message = PubsubMessage(data=data, ordering_key=ordering_key, attributes=attrs)
    psl_message = from_cps_publish_message(cps_message)
    return (await self._publisher.publish(psl_message)).encode()

  def __aenter__(self):
    self._publisher.__aenter__()
    return self

  def __aexit__(self, exc_type, exc_value, traceback):
    self._publisher.__aexit__(exc_type, exc_value, traceback)
