from abc import abstractmethod
from typing import AsyncContextManager
from google.cloud.pubsublite_v1.types import SequencedMessage, FlowControlRequest


class Subscriber(AsyncContextManager):
    """
  A Pub/Sub Lite asynchronous wire protocol subscriber.
  """

    @abstractmethod
    async def read(self) -> SequencedMessage:
        """
    Read the next message off of the stream.

    Returns:
      The next message.

    Raises:
      GoogleAPICallError: On a permanent error.
    """
        raise NotImplementedError()

    @abstractmethod
    async def allow_flow(self, request: FlowControlRequest):
        """
    Allow an additional amount of messages and bytes to be sent to this client.
    """
        raise NotImplementedError()
