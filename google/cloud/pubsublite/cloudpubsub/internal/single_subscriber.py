from abc import abstractmethod
from typing import AsyncContextManager, Callable, Set, Optional

from google.cloud.pubsub_v1.subscriber.message import Message

from google.cloud.pubsublite.types import (
    SubscriptionPath,
    FlowControlSettings,
    Partition,
)


class AsyncSingleSubscriber(AsyncContextManager):
    """
  A Cloud Pub/Sub asynchronous subscriber.

  Must be used in an `async with` block or have __aenter__() awaited before use.
  """

    @abstractmethod
    async def read(self) -> Message:
        """
    Read the next message off of the stream.

    Returns:
      The next message. ack() or nack() must eventually be called exactly once.

      Pub/Sub Lite does not support nack() by default- if you do call nack(), it will immediately fail the client
      unless you have a NackHandler installed.

    Raises:
      GoogleAPICallError: On a permanent error.
    """
        raise NotImplementedError()


AsyncSubscriberFactory = Callable[
    [SubscriptionPath, Optional[Set[Partition]], FlowControlSettings],
    AsyncSingleSubscriber,
]
