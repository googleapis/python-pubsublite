from abc import ABC, abstractmethod
from google.cloud.pubsublite_v1.types import PubSubMessage
from google.cloud.pubsublite.publish_metadata import PublishMetadata


class Publisher(ABC):
  """
  A Pub/Sub Lite asynchronous wire protocol publisher.
  """
  @abstractmethod
  async def __aenter__(self):
    raise NotImplementedError()

  @abstractmethod
  async def __aexit__(self, exc_type, exc_val, exc_tb):
    raise NotImplementedError()

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
