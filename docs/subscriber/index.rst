Subscriber Client
=================

Subscribe operations are handled through the
:class:`~.pubsublite.cloudpubsub.subscriber_client.SubscriberClient` class (aliased as
``google.cloud.pubsublite.cloudpubsub.SubscriberClient``).

You should instantiate a subscriber client using a context manager:

.. code-block:: python

    from google.cloud.pubsublite.cloudpubsub import SubscriberClient

    with SubscriberClient() as subscriber_client:
        # Use subscriber_client

When not using a context manager, you need to call
:meth:`~.pubsublite.cloudpubsub.subscriber_client.SubscriberClient.__enter__`.

Receive messages
----------------

To receive messages, use the
:meth:`~.pubsublite.cloudpubsub.subscriber_client.SubscriberClient.subscribe`
method. This method requires
three positional arguments: a :class:`~.pubsublite.types.SubscriptionPath` object,
a callback function, and a :class:`~.pubsublite.types.FlowControlSettings` object.

Receiving messages looks like:

.. code-block:: python

    from google.cloud.pubsublite.cloudpubsub import SubscriberClient
    from google.cloud.pubsublite.types import (
        CloudRegion,
        CloudZone,
        SubscriptionPath,
        DISABLED_FLOW_CONTROL,
    )

    project_number = 1122334455
    cloud_region = "us-central1"
    zone_id = "a"
    subscription_id = "your-subscription-id"

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    subscription_path = SubscriptionPath(project_number, location, subscription_id)

    with SubscriberClient() as subscriber_client:
        streaming_pull_future = subscriber_client.subscribe(
            subscription_path,
            callback=callback,
            per_partition_flow_control_settings=DISABLED_FLOW_CONTROL,
        )

        streaming_pull_future.result()

Subscriber Callbacks
--------------------

Received messages are processed in a callback function. This callback function
only takes one argument of type :class:`google.cloud.pubsub_v1.subscriber.message.Message`.
After this message has been processed, the function should either call
:meth:`~.pubsub_v1.subscriber.message.Message.ack` to acknowledge the message or
:meth:`~.pubsub_v1.subscriber.message.Message.nack` to send a negative acknowledgement.

.. code-block:: python

    def callback(message):
        message_data = message.data.decode("utf-8")
        print(f"Received {message_data}.")
        message.ack()

Flow Control Settings
---------------------

Flow control settings are applied per partition.
They control when to pause the message stream to a partition so the server temporarily
stops sending out more messages (known as outstanding messages) from this partition.

You can configure flow control settings by setting the maximum number and size of
outstanding messages. The message stream is paused when either condition is met.

.. code-block:: python

    from google.cloud.pubsublite.types import FlowControlSettings

    flow_control_settings = FlowControlSettings(
        # 1,000 outstanding messages. Must be >0.
        messages_outstanding=1000,
        # 10 MiB. Must be greater than the allowed size of the largest message (1 MiB).
        bytes_outstanding=10 * 1024 * 1024,
    )

You may also turn off flow control settings by setting it to
:class:`google.cloud.pubsublite.types.DISABLED_FLOW_CONTROL`.

API Reference
-------------

.. toctree::
  :maxdepth: 2

  api/client
