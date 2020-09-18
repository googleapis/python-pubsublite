from abc import abstractmethod
from typing import AsyncContextManager


class AckSetTracker(AsyncContextManager):
  """
  An AckSetTracker tracks disjoint acknowledged messages and commits them when necessary.
  """
  @abstractmethod
  def track(self, offset: int):
    """
    Track the provided offset.

    Args:
      offset: the offset to track.

    Raises:
      GoogleAPICallError: On an invalid offset to track.
    """

  @abstractmethod
  async def ack(self, offset: int):
    """
    Acknowledge the message with the provided offset. The offset must have previously been tracked.

    Args:
      offset: the offset to acknowledge.

    Returns:
      GoogleAPICallError: On a commit failure.
    """