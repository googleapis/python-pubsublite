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

import pytest

from mock import MagicMock, call

# All test coroutines will be treated as marked.
from google.api_core.exceptions import FailedPrecondition

from google.cloud.pubsublite.cloudpubsub.internal.client_multiplexer import (
    ClientMultiplexer,
)


class Client:
    pass


@pytest.fixture()
def client_factory():
    return MagicMock()


@pytest.fixture()
def client_closer():
    return MagicMock()


@pytest.fixture()
def multiplexer(client_closer):
    return ClientMultiplexer(client_closer)


def test_create(
    multiplexer: ClientMultiplexer[int, Client], client_closer, client_factory
):
    client1 = Client()
    client2 = Client()
    with multiplexer:
        client_factory.return_value = client1
        assert multiplexer.create_or_fail(1, client_factory) is client1
        client_factory.assert_has_calls([call()])
        client_factory.return_value = client2
        assert multiplexer.get_or_create(1, client_factory) is client1
        with pytest.raises(FailedPrecondition):
            multiplexer.create_or_fail(1, client_factory)
        assert multiplexer.get_or_create(2, client_factory) is client2
        client_factory.assert_has_calls([call(), call()])
        with pytest.raises(FailedPrecondition):
            multiplexer.create_or_fail(2, client_factory)
    client_closer.assert_has_calls([call(client1), call(client2)], any_order=True)


def test_recreate(
    multiplexer: ClientMultiplexer[int, Client], client_closer, client_factory
):
    client1 = Client()
    client2 = Client()
    with multiplexer:
        client_factory.return_value = client1
        assert multiplexer.create_or_fail(1, client_factory) is client1
        client_factory.assert_has_calls([call()])
        client_factory.return_value = client2
        multiplexer.try_erase(1, client2)
        client_closer.assert_has_calls([])
        multiplexer.try_erase(1, client1)
        client_closer.assert_has_calls([call(client1)])
        assert multiplexer.create_or_fail(1, client_factory) is client2
    client_closer.assert_has_calls([call(client1), call(client2)])
