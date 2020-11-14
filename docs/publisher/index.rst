Publisher Client
================

Publish operations are handled through the
:class:`~.pubsublite.cloudpubsub.publisher_client.PublisherClient` class (aliased as
``google.cloud.pubsublite.cloudpubsub.PublisherClient``).

You should instantiate a publisher client using a context manager:

.. code-block:: python

    from google.cloud.pubsublite.cloudpubsub import PublisherClient

    with PublisherClient() as publisher_client:
        pass

When not using a context manager, you need to call
:meth:`~.pubsublite.cloudpubsub.publisher_client.PublisherClient.__enter__`.

Publish a message
-----------------

To publish a message, use the
:meth:`~.pubsublite.cloudpubsub.publisher_client.PublisherClient.publish`
method. This method accepts
two positional arguments: a :class:`~.pubsublite.types.TopicPath` object
and a message in byte string.

A call to publish a message looks like:

.. code-block:: python

    from google.cloud.pubsublite.types import (
        CloudRegion, CloudZone, TopicPath,
    )

    project_number = 1122334455
    cloud_region = "us-central1"
    zone_id = "a"
    topic_id = "your-topic-id"

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    topic_path = TopicPath(project_number, location, topic_id)

    with PublisherClient() as publisher_client:
        data = "Hello world!"
        api_future = publisher_client.publish(t
            opic_path, data.encode("utf-8")
        )
        message_id = api_future.result()


API Reference
-------------

.. toctree::
  :maxdepth: 2

  api/client
