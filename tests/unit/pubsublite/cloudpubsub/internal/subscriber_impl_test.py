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

import asyncio
import concurrent
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue

from asynctest.mock import MagicMock
import pytest
from google.api_core.exceptions import FailedPrecondition
from google.cloud.pubsub_v1.subscriber.message import Message
from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub.internal.streaming_pull_manager import (
    CloseCallback,
)
from google.cloud.pubsublite.cloudpubsub.internal.subscriber_impl import SubscriberImpl
from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSingleSubscriber,
)
from google.cloud.pubsublite.cloudpubsub.subscriber_client_interface import (
    MessageCallback,
)
from google.cloud.pubsublite.testing.test_utils import Box


@pytest.fixture()
def async_subscriber():
    subscriber = MagicMock(spec=AsyncSingleSubscriber)
    subscriber.__aenter__.return_value = subscriber
    return subscriber


@pytest.fixture()
def message_callback():
    return MagicMock(spec=MessageCallback)


@pytest.fixture()
def close_callback():
    return MagicMock(spec=CloseCallback)


@pytest.fixture()
def subscriber(async_subscriber, message_callback, close_callback):
    return SubscriberImpl(
        async_subscriber, message_callback, ThreadPoolExecutor(max_workers=1)
    )


async def sleep_forever(*args, **kwargs):
    await asyncio.sleep(float("inf"))


def test_init(subscriber: SubscriberImpl, async_subscriber, close_callback):
    async_subscriber.read.side_effect = sleep_forever
    subscriber.add_close_callback(close_callback)
    subscriber.__enter__()
    async_subscriber.__aenter__.assert_called_once()
    subscriber.close()
    async_subscriber.__aexit__.assert_called_once()
    close_callback.assert_called_once_with(subscriber, None)


def test_failed(subscriber: SubscriberImpl, async_subscriber, close_callback):
    error = FailedPrecondition("bad read")
    async_subscriber.read.side_effect = error

    close_called = concurrent.futures.Future()
    close_callback.side_effect = lambda manager, err: close_called.set_result(None)

    subscriber.add_close_callback(close_callback)
    subscriber.__enter__()
    async_subscriber.__aenter__.assert_called_once()
    close_called.result()
    async_subscriber.__aexit__.assert_called_once()
    close_callback.assert_called_once_with(subscriber, error)


def test_messages_received(
    subscriber: SubscriberImpl, async_subscriber, message_callback, close_callback
):
    message1 = Message(PubsubMessage(message_id="1")._pb, "", 0, None)
    message2 = Message(PubsubMessage(message_id="2")._pb, "", 0, None)

    counter = Box[int]()
    counter.val = 0

    async def on_read() -> Message:
        counter.val += 1
        if counter.val == 1:
            return message1
        if counter.val == 2:
            return message2
        await sleep_forever()

    async_subscriber.read.side_effect = on_read

    results = Queue()
    message_callback.side_effect = lambda m: results.put(m.message_id)

    subscriber.add_close_callback(close_callback)
    subscriber.__enter__()
    assert results.get() == "1"
    assert results.get() == "2"
    subscriber.close()
