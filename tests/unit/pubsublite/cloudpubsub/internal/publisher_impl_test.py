from asynctest.mock import MagicMock
import pytest

from google.cloud.pubsublite.cloudpubsub.internal.publisher_impl import (
    SinglePublisherImpl,
)
from google.cloud.pubsublite.cloudpubsub.internal.single_publisher import (
    AsyncSinglePublisher,
    SinglePublisher,
)


@pytest.fixture()
def async_publisher():
    publisher = MagicMock(spec=AsyncSinglePublisher)
    publisher.__aenter__.return_value = publisher
    return publisher


@pytest.fixture()
def publisher(async_publisher):
    return SinglePublisherImpl(async_publisher)


def test_proxies_to_async(async_publisher, publisher: SinglePublisher):
    with publisher:
        async_publisher.__aenter__.assert_called_once()
        publisher.publish(data=b"abc", ordering_key="zyx", xyz="xyz").result()
        async_publisher.publish.assert_called_once_with(
            data=b"abc", ordering_key="zyx", xyz="xyz"
        )
    async_publisher.__aexit__.assert_called_once()
