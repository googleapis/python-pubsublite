from typing import NamedTuple
from google.cloud.pubsublite_v1.types.common import Cursor
from google.cloud.pubsublite.partition import Partition


class PublishMetadata(NamedTuple):
    partition: Partition
    cursor: Cursor
