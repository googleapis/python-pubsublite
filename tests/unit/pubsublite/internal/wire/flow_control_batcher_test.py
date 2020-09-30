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
