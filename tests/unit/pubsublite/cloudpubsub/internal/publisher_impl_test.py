from asynctest.mock import MagicMock
import pytest

from google.cloud.pubsublite.cloudpubsub.internal.publisher_impl import PublisherImpl
from google.cloud.pubsublite.cloudpubsub.publisher import AsyncPublisher, Publisher


@pytest.fixture()
def async_publisher():
  publisher = MagicMock(spec=AsyncPublisher)
  publisher.__aenter__.return_value = publisher
  return publisher


@pytest.fixture()
def publisher(async_publisher):
  return PublisherImpl(async_publisher)


def test_proxies_to_async(async_publisher, publisher: Publisher):
  with publisher:
    async_publisher.__aenter__.assert_called_once()
    publisher.publish(data=b'abc', ordering_key='zyx', xyz='xyz').result()
    async_publisher.publish.assert_called_once_with(data=b'abc', ordering_key='zyx', xyz='xyz')
  async_publisher.__aexit__.assert_called_once()
