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

from google.cloud.pubsublite.internal.wire.flow_control_batcher import (
    FlowControlBatcher,
)
from google.cloud.pubsublite_v1 import FlowControlRequest, SequencedMessage


def test_restart_clears_send():
    batcher = FlowControlBatcher()
    batcher.add(FlowControlRequest(allowed_bytes=10, allowed_messages=3))
    assert batcher.should_expedite()
    to_send = batcher.release_pending_request()
    assert to_send.allowed_bytes == 10
    assert to_send.allowed_messages == 3
    restart_1 = batcher.request_for_restart()
    assert restart_1.allowed_bytes == 10
    assert restart_1.allowed_messages == 3
    assert not batcher.should_expedite()
    assert batcher.release_pending_request() is None


def test_add_remove():
    batcher = FlowControlBatcher()
    batcher.add(FlowControlRequest(allowed_bytes=10, allowed_messages=3))
    restart_1 = batcher.request_for_restart()
    assert restart_1.allowed_bytes == 10
    assert restart_1.allowed_messages == 3
    batcher.on_messages(
        [SequencedMessage(size_bytes=2), SequencedMessage(size_bytes=3)]
    )
    restart_2 = batcher.request_for_restart()
    assert restart_2.allowed_bytes == 5
    assert restart_2.allowed_messages == 1
