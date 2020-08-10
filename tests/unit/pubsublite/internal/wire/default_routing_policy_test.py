import json
import os

from google.cloud.pubsublite.partition import Partition

from google.cloud.pubsublite.internal.wire.default_routing_policy import DefaultRoutingPolicy
from google.cloud.pubsublite_v1 import PubSubMessage


def test_routing_cases():
  policy = DefaultRoutingPolicy(num_partitions=29)
  json_list = []
  with open(os.path.join(os.path.dirname(__file__), "routing_tests.json")) as f:
    for line in f:
      if not line.startswith("//"):
        json_list.append(line)

  loaded = json.loads("\n".join(json_list))
  target = {bytes(k, 'utf-8'): Partition(v) for k, v in loaded.items()}
  result = {}
  for key in target:
    result[key] = policy.route(PubSubMessage(key=key))
  assert result == target
