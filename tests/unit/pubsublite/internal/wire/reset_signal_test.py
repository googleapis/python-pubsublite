# Copyright 2021 Google LLC
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

import pytest
from google.api_core.exceptions import Aborted, NotFound
from google.cloud.pubsublite.internal.wire.reset_signal import is_reset_signal
from google.cloud.pubsublite.testing.test_reset_signal import (
    make_call,
    make_call_without_metadata,
    make_reset_signal,
)
from google.protobuf.any_pb2 import Any
from google.rpc.error_details_pb2 import ErrorInfo, RetryInfo
from google.rpc.status_pb2 import Status

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_is_reset_signal():
    assert is_reset_signal(make_reset_signal())


async def test_non_retryable():
    assert not is_reset_signal(NotFound(""))


async def test_missing_call():
    assert not is_reset_signal(Aborted(""))


async def test_extracted_status_is_none():
    status_pb = Status(code=10, details=[])
    assert not is_reset_signal(
        Aborted("", response=make_call_without_metadata(status_pb))
    )


async def test_wrong_reason():
    any = Any()
    any.Pack(ErrorInfo(reason="OTHER", domain="pubsublite.googleapis.com"))
    status_pb = Status(code=10, details=[any])
    assert not is_reset_signal(Aborted("", response=make_call(status_pb)))


async def test_wrong_domain():
    any = Any()
    any.Pack(ErrorInfo(reason="RESET", domain="other.googleapis.com"))
    status_pb = Status(code=10, details=[any])
    assert not is_reset_signal(Aborted("", response=make_call(status_pb)))


async def test_wrong_error_detail():
    any = Any()
    any.Pack(RetryInfo())
    status_pb = Status(code=10, details=[any])
    assert not is_reset_signal(Aborted("", response=make_call(status_pb)))


async def test_other_error_details_present():
    any1 = Any()
    any1.Pack(RetryInfo())
    any2 = Any()
    any2.Pack(ErrorInfo(reason="RESET", domain="pubsublite.googleapis.com"))
    status_pb = Status(code=10, details=[any1, any2])
    assert is_reset_signal(Aborted("", response=make_call(status_pb)))
