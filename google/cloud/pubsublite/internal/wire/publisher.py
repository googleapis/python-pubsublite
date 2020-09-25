from abc import abstractmethod
from typing import AsyncContextManager
from google.cloud.pubsublite_v1.types import PubSubMessage
from google.cloud.pubsublite.publish_metadata import PublishMetadata


class Publisher(AsyncContextManager):
    """
  A Pub/Sub Lite asynchronous wire protocol publisher.
  """

    @abstractmethod
    async def publish(self, message: PubSubMessage) -> PublishMetadata:
        """
    Publish the provided message.

    Args:
      message: The message to be published.

    Returns:
      Metadata about the published message.

    Raises:
      GoogleAPICallError: On a permanent error.
    """
        raise NotImplementedError()
