from typing import NamedTuple
import json

from google.cloud.pubsublite_v1.types.common import Cursor
from google.cloud.pubsublite.types.partition import Partition


class PublishMetadata(NamedTuple):
    partition: Partition
    cursor: Cursor

    def encode(self) -> str:
        return json.dumps(
            {"partition": self.partition.value, "offset": self.cursor.offset}
        )

    @staticmethod
    def decode(source: str) -> "PublishMetadata":
        loaded = json.loads(source)
        return PublishMetadata(
            partition=Partition(loaded["partition"]),
            cursor=Cursor(offset=loaded["offset"]),
        )
