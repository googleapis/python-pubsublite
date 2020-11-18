Admin Operations
================

Admin operations are handled through the
:class:`~.pubsublite.admin_client.AdminClient` class (aliased as
``google.cloud.pubsublite.AdminClient``).

Instantiating an admin client requires you to provide a valid cloud region
for the Pub/Sub Lite service:

.. code-block:: python

    from google.cloud.pubsublite import AdminClient
    cloud_region = CloudRegion("us-central1")
    admin_client = AdminClient(cloud_region)


Create a topic
--------------

To create a message, use the
:meth:`~.pubsublite.admin_client.AdminClient.create_topic` method. This method accepts
one positional arguments: a :class:`~.pubsublite_v1.types.Topic` object, where the name
of the topic is passed along as a string.

Pub/Sub Lite topics have the canonical form of

    ``projects/{project_number}/locations/{location}/topics/{topic_id}``

A location (a.k.a. `zone`_) is comprised of a cloud region and a zone ID.

.. _zone: https://cloud.google.com/pubsub/lite/docs/locations/

A call to create a Pub/Sub Lite topic looks like:

.. code-block:: python

    from google.cloud.pubsublite import AdminClient, Topic
    from google.cloud.pubsublite.types import (
        CloudRegion, CloudZone, TopicPath,
    )

    project_number = 1122334455
    zone_id = "a"
    topic_id = "your-topic-id"

    cloud_region = CloudRegion(cloud_region)
    location = CloudZone(cloud_region, zone_id)
    topic_path = TopicPath(project_number, location, topic_id)

    topic = Topic(
        name=str(topic_path),
        partition_config=Topic.PartitionConfig(
            # 1 partition
            count=1,
            # Publish at 4 MiB/s and subscribe at 8 MiB/s
            capacity=Topic.PartitionConfig.Capacity(
                publish_mib_per_sec=4,
                subscribe_mib_per_sec=8,
            ),
        ),
        retention_config=Topic.RetentionConfig(
            # 30 GiB
            per_partition_bytes=30 * 1024 * 1024 * 1024,
            # 7 days
            period=Duration(seconds=60 * 60 * 24 * 7),
        ),
    )

    admin_client = AdminClient(cloud_region)
    response = admin_client.create_topic(topic)


API Reference
-------------

.. toctree::
  :maxdepth: 2

  api/client
