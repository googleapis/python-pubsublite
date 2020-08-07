import asyncio
from typing import Union
from unittest.mock import call

import pytest
from asynctest import MagicMock, CoroutineMock
from google.cloud.pubsublite.internal.wire.aggregator import Aggregator, RequestSender
from google.cloud.pubsublite.testing.test_utils import make_queue_waiter, Box

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

SLEEP_SECS = 1000


@pytest.fixture()
def sender():
  return MagicMock(spec=RequestSender[int, int])


@pytest.fixture()
def aggregator(sender):
  return Aggregator[int, int](sender, SLEEP_SECS)


@pytest.fixture
def sleep_called():
  return asyncio.Queue()


@pytest.fixture()
def sleep_results():
  return asyncio.Queue()


@pytest.fixture
def asyncio_sleep(monkeypatch, sleep_called, sleep_results):
  """Requests.get() mocked to return {'mock_key':'mock_response'}."""
  mock = CoroutineMock()
  monkeypatch.setattr(asyncio, "sleep", mock)
  mock.side_effect = make_queue_waiter(sleep_called, sleep_results)
  return mock


async def test_sends_batches(asyncio_sleep, sleep_called, sleep_results, sender, aggregator):
  async with aggregator:
    await sleep_called.get()  # Wait for the aggregator to sleep
    asyncio_sleep.assert_has_calls([call(SLEEP_SECS)])
    fut1 = asyncio.ensure_future(aggregator.push(1))
    fut2 = asyncio.ensure_future(aggregator.push(2))
    sender.send.return_value = [5, 6]
    await sleep_results.put(None)
    await sleep_called.get()  # Wait for the aggregator to sleep again
    fut3 = asyncio.ensure_future(aggregator.push(3))
    fut4 = asyncio.ensure_future(aggregator.push(4))
    sender.send.return_value = [7, 8]
    await sleep_results.put(None)
    await sleep_called.get()  # Wait for the aggregator to sleep again
    sender.send.assert_has_calls([call([1, 2]), call([3, 4])])
    assert await fut1 == 5
    assert await fut2 == 6
    assert await fut3 == 7
    assert await fut4 == 8


async def test_restart(asyncio_sleep, sleep_called, sleep_results, sender, aggregator):
  async with aggregator:
    await sleep_called.get()  # Wait for the aggregator to sleep
    fut1 = asyncio.ensure_future(aggregator.push(1))
    async def noreturn():
      await asyncio.Future()
    sender.send.side_effect = noreturn
    await sleep_results.put(None)
    await sleep_called.get()  # Wait for the aggregator to sleep
    sender.send.assert_has_calls([call([1])])
    fut2 = asyncio.ensure_future(aggregator.push(2))
    sender.send.side_effect = [[3], [4]]
    await aggregator.restart()
    await sleep_called.get()  # Wait for the aggregator to sleep
    sender.send.assert_has_calls([call([1]), call([1]), call([2])])
    assert await fut1 == 3
    assert await fut2 == 4


async def test_aexit_sends(asyncio_sleep, sleep_called, sleep_results, sender, aggregator):
  fut1 = Box[asyncio.Future]()
  async with aggregator:
    await sleep_called.get()  # Wait for the aggregator to sleep
    fut1.val = asyncio.ensure_future(aggregator.push(1))
    sender.send.return_value = [2]
  sender.send.assert_has_calls([call([1])])
  assert await fut1.val == 2
