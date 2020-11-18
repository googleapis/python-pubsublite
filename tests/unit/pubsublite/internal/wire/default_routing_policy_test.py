# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

from google.cloud.pubsublite.types import Partition

from google.cloud.pubsublite.internal.wire.default_routing_policy import (
    DefaultRoutingPolicy,
)
from google.cloud.pubsublite_v1 import PubSubMessage


def test_routing_cases():
    policy = DefaultRoutingPolicy(num_partitions=29)
    json_list = []
    with open(os.path.join(os.path.dirname(__file__), "routing_tests.json")) as f:
        for line in f:
            if not line.startswith("//"):
                json_list.append(line)

    loaded = json.loads("\n".join(json_list))
    target = {bytes(k, "utf-8"): Partition(v) for k, v in loaded.items()}
    result = {}
    for key in target:
        result[key] = policy.route(PubSubMessage(key=key))
    assert result == target
