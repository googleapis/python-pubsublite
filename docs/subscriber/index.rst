Subscriber Client
=================

Subscribe operations are handled through the
:class:`~.pubsublite.cloudpubsub.subscriber_client.SubscriberClient` class (aliased as
``google.cloud.pubsublite.cloudpubsub.SubscriberClient``).

Instantiating a subscriber client is simple:

.. code-block:: python

    from google.cloud.pubsublite.cloudpubsub import SubscriberClient

    subscriber_client = SubscriberClient()

Receive messages
----------------

To receive messages, use the
:meth:`~.pubsublite.cloudpubsub.subscriber_client.SubscriberClient.subscribe`
method. This method requires
three positional arguments: a :class:`~.pubsublite.types.SubscriptionPath` object,
a callback function, and a :class:`~.pubsublite.types.FlowControlSettings` object.

Receiving messages looks like:

.. code-block:: python

    from concurrent.futures._base import TimeoutError
    from google.cloud.pubsublite.types import (
        CloudRegion,
        CloudZone,
        FlowControlSettings,
        SubscriptionPath,
    )

    project_number = 1122334455
    cloud_region = "us-central1"
    zone_id = "a"
    subscription_id = "your-subscription-id"

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    subscription_path = SubscriptionPath(project_number, location, subscription_id)

    streaming_pull_future = subscriber_client.subscribe(
        subscription_path,
        callback=callback,
        per_partition_flow_control_settings=flow_control_settings,
    )

    streaming_pull_future.result()

Subscriber Callbacks
--------------------

Received messages are processed in a callback function. This callback function
only takes one argument of type :class:`google.cloud.pubsub_v1.subscriber.message.Message`.
After this message has been processed, the function should call either call
:meth:`~.pubsub_v1.subscriber.message.Message.ack` to acknowledge the message
or :meth:`~.pubsub_v1.subscriber.message.Message.nack` to unacknowledge the message.

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
outstanding messages. The message stream is paused when either condition is met first.


.. code-block:: python

    flow_control_settings = FlowControlSettings(
        # 1,000 outstanding messages. Must be >0.
        messages_outstanding=1000,
        # 10 MiB. Must be greater than the allowed size of the largest message (1 MiB).
        bytes_outstanding=10 * 1024 * 1024,
    )

API Reference
-------------

.. toctree::
  :maxdepth: 2

  api/client
