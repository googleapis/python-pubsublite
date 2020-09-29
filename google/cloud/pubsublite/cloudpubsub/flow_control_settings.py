from typing import NamedTuple


class FlowControlSettings(NamedTuple):
    messages_outstanding: int
    bytes_outstanding: int


_MAX_INT64 = 0x7FFFFFFFFFFFFFFF

DISABLED_FLOW_CONTROL = FlowControlSettings(_MAX_INT64, _MAX_INT64)
