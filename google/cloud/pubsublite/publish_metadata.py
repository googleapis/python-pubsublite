from typing import NamedTuple, cast

from google.cloud.pubsublite.internal.b64_utils import to_b64_string, from_b64_string
from google.cloud.pubsublite_v1.types.common import Cursor
from google.cloud.pubsublite.partition import Partition


class PublishMetadata(NamedTuple):
  partition: Partition
  cursor: Cursor

  def encode(self) -> str:
    return to_b64_string(self)

  @staticmethod
  def decode(source: str) -> 'PublishMetadata':
    return cast(PublishMetadata, from_b64_string(source))
