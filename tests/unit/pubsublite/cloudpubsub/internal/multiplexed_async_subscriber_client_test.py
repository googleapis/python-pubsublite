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

import pytest

from asynctest.mock import call, MagicMock

from google.api_core.exceptions import FailedPrecondition
from google.cloud.pubsub_v1.subscriber.message import Message
from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub import AsyncSubscriberClientInterface

# All test coroutines will be treated as marked.
from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_async_subscriber_client import (
    MultiplexedAsyncSubscriberClient,
)
from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSubscriberFactory,
    AsyncSingleSubscriber,
)
from google.cloud.pubsublite.testing.test_utils import wire_queues
from google.cloud.pubsublite.types import (
    SubscriptionPath,
    CloudZone,
    DISABLED_FLOW_CONTROL,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def default_subscriber():
    return MagicMock(spec=AsyncSingleSubscriber)


@pytest.fixture()
def subscriber_factory(default_subscriber):
    factory = MagicMock(spec=AsyncSubscriberFactory)
    factory.return_value = default_subscriber
    return factory


@pytest.fixture()
def multiplexed_client(subscriber_factory: AsyncSubscriberFactory):
    return MultiplexedAsyncSubscriberClient(subscriber_factory)


async def test_iterator(
    default_subscriber,
    subscriber_factory,
    multiplexed_client: AsyncSubscriberClientInterface,
):
    read_queues = wire_queues(default_subscriber.read)
    subscription = SubscriptionPath(1, CloudZone.parse("us-central1-a"), "abc")
    message = Message(PubsubMessage(message_id="1")._pb, "", 0, None)
    async with multiplexed_client:
        iterator = await multiplexed_client.subscribe(
            subscription, DISABLED_FLOW_CONTROL
        )
        subscriber_factory.assert_has_calls(
            [call(subscription, None, DISABLED_FLOW_CONTROL)]
        )
        read_fut_1 = asyncio.ensure_future(iterator.__anext__())
        assert not read_fut_1.done()
        await read_queues.called.get()
        default_subscriber.read.assert_has_calls([call()])
        await read_queues.results.put(message)
        assert await read_fut_1 is message
        read_fut_2 = asyncio.ensure_future(iterator.__anext__())
        assert not read_fut_2.done()
        await read_queues.called.get()
        default_subscriber.read.assert_has_calls([call(), call()])
        await read_queues.results.put(FailedPrecondition(""))
        with pytest.raises(FailedPrecondition):
            await read_fut_2
        default_subscriber.__aexit__.assert_called_once()
