from abc import abstractmethod
from typing import AsyncContextManager, Mapping, ContextManager
from concurrent import futures


class AsyncPublisher(AsyncContextManager):
    """
  An AsyncPublisher publishes messages similar to Google Pub/Sub, but must be used in an
  async context. Any publish failures are permanent.

  Must be used in an `async with` block or have __aenter__() awaited before use.
  """

    @abstractmethod
    async def publish(
        self, data: bytes, ordering_key: str = "", **attrs: Mapping[str, str]
    ) -> str:
        """
    Publish a message.

    Args:
      data: The bytestring payload of the message
      ordering_key: The key to enforce ordering on, or "" for no ordering.
      **attrs: Additional attributes to send.

    Returns:
      An ack id, which can be decoded using PublishMetadata.decode.

    Raises:
      GoogleApiCallError: On a permanent failure.
    """


class Publisher(ContextManager):
    """
  A Publisher publishes messages similar to Google Pub/Sub. Any publish failures are permanent.

  Must be used in a `with` block or have __enter__() called before use.
  """

    @abstractmethod
    def publish(
        self, data: bytes, ordering_key: str = "", **attrs: Mapping[str, str]
    ) -> "futures.Future[str]":
        """
    Publish a message.

    Args:
      data: The bytestring payload of the message
      ordering_key: The key to enforce ordering on, or "" for no ordering.
      **attrs: Additional attributes to send.

    Returns:
      A future completed with an ack id, which can be decoded using PublishMetadata.decode.

    Raises:
      GoogleApiCallError: On a permanent failure.
    """
