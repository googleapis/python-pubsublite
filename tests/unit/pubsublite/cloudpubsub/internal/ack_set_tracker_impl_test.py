from asynctest.mock import MagicMock, call
import pytest

# All test coroutines will be treated as marked.
from google.cloud.pubsublite.cloudpubsub.internal.ack_set_tracker import AckSetTracker
from google.cloud.pubsublite.cloudpubsub.internal.ack_set_tracker_impl import AckSetTrackerImpl
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
    await tracker.ack(offset=5)
    committer.commit.assert_has_calls([])
    await tracker.ack(offset=1)
    committer.commit.assert_has_calls([call(Cursor(offset=6))])

    tracker.track(offset=8)
    await tracker.ack(offset=7)
    committer.commit.assert_has_calls([call(Cursor(offset=6)), call(Cursor(offset=8))])
  committer.__aexit__.assert_called_once()


