from abc import ABC, abstractmethod
from typing import Callable

from google.api_core.exceptions import FailedPrecondition
from google.pubsub_v1 import PubsubMessage


class NackHandler(ABC):
  """
  A NackHandler handles calls to the nack() method which is not expressible in Pub/Sub Lite.
  """

  @abstractmethod
  def on_nack(self, message: PubsubMessage, ack: Callable[[], None]):
    """Handle a negative acknowledgement. ack must eventually be called.

    Args:
      message: The nacked message.
      ack: A callable to acknowledge the underlying message. This must eventually be called.

    Raises:
      GoogleAPICallError: To fail the client if raised inline.
    """
    pass


class DefaultNackHandler(NackHandler):
  def on_nack(self, message: PubsubMessage, ack: Callable[[], None]):
    raise FailedPrecondition(
      "You may not nack messages by default when using a PubSub Lite client. See NackHandler for how to customize"
      " this.")
