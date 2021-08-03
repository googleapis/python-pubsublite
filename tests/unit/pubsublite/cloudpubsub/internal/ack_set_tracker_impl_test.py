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

from asynctest.mock import MagicMock, call
import pytest

from google.api_core.exceptions import FailedPrecondition

# All test coroutines will be treated as marked.
from google.cloud.pubsublite.cloudpubsub.internal.ack_set_tracker import AckSetTracker
from google.cloud.pubsublite.cloudpubsub.internal.ack_set_tracker_impl import (
    AckSetTrackerImpl,
)
from google.cloud.pubsublite.internal.wire.committer import Committer
from google.cloud.pubsublite_v1 import Cursor

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def committer():
    committer = MagicMock(spec=Committer)
    committer.__aenter__.return_value = committer
    return committer


@pytest.fixture()
def tracker(committer):
    return AckSetTrackerImpl(committer)


async def test_track_and_aggregate_acks(committer, tracker: AckSetTracker):
    async with tracker:
        committer.__aenter__.assert_called_once()
        tracker.track(offset=1)
        tracker.track(offset=3)
        tracker.track(offset=5)
        tracker.track(offset=7)

        committer.commit.assert_has_calls([])
        await tracker.ack(offset=3)
        committer.commit.assert_has_calls([])
        await tracker.ack(offset=1)
        committer.commit.assert_has_calls([call(Cursor(offset=4))])
        await tracker.ack(offset=5)
        committer.commit.assert_has_calls(
            [call(Cursor(offset=4)), call(Cursor(offset=6))]
        )

        tracker.track(offset=8)
        await tracker.ack(offset=7)
        committer.commit.assert_has_calls(
            [call(Cursor(offset=4)), call(Cursor(offset=6)), call(Cursor(offset=8))]
        )
    committer.__aexit__.assert_called_once()


async def test_clear_and_commit(committer, tracker: AckSetTracker):
    async with tracker:
        committer.__aenter__.assert_called_once()
        tracker.track(offset=3)
        tracker.track(offset=5)

        with pytest.raises(FailedPrecondition):
            tracker.track(offset=1)
        await tracker.ack(offset=5)
        committer.commit.assert_has_calls([])

        await tracker.clear_and_commit()
        committer.wait_until_empty.assert_called_once()

        # After clearing, it should be possible to track earlier offsets.
        tracker.track(offset=1)
        await tracker.ack(offset=1)
        committer.commit.assert_has_calls([call(Cursor(offset=2))])
    committer.__aexit__.assert_called_once()
