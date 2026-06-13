# Copyright 2026 Google LLC
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

import sys
from unittest.mock import MagicMock
import pytest

# Create a single shared mock for confluent_kafka to avoid test isolation issues
# due to lazy imports and module caching.
shared_mock_confluent_kafka = MagicMock()
sys.modules["confluent_kafka"] = shared_mock_confluent_kafka


@pytest.fixture(autouse=True)
def reset_confluent_kafka():
    shared_mock_confluent_kafka.reset_mock()
    shared_mock_confluent_kafka.Producer = MagicMock()
    shared_mock_confluent_kafka.Consumer = MagicMock()
    # TopicPartition needs to be a callable that returns a mock, or just a mock class.
    # We use MagicMock as it behaves like a class when called.
    shared_mock_confluent_kafka.TopicPartition = MagicMock


@pytest.fixture()
def confluent_kafka_mock():
    return shared_mock_confluent_kafka
