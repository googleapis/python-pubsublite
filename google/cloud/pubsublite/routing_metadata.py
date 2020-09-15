from typing import Mapping, Union
from urllib.parse import urlencode

from google.cloud.pubsublite.partition import Partition
from google.cloud.pubsublite.paths import TopicPath, SubscriptionPath

_PARAMS_HEADER = "x-goog-request-params"


def topic_routing_metadata(topic: TopicPath, partition: Partition) -> Mapping[str, str]:
  encoded = urlencode(topic)
  return {_PARAMS_HEADER: f"partition={partition.value}&topic={encoded}"}


def subscription_routing_metadata(subscription: SubscriptionPath, partition: Partition) -> Mapping[str, str]:
  encoded = urlencode(subscription)
  return {_PARAMS_HEADER: f"partition={partition.value}&subscription={encoded}"}
