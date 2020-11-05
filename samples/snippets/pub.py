from concurrent.futures._base import TimeoutError
from google.cloud.pubsublite.cloudpubsub import PublisherClient, SubscriberClient
#, SubscriberClient
from google.cloud.pubsublite.types import (
        CloudRegion,
        CloudZone,
        FlowControlSettings,
        PublishMetadata,
        SubscriptionPath,
        TopicPath,
    )
from google.cloud.pubsub_v1.types import BatchSettings
from google.api_core.exceptions import Cancelled


# TODO(developer):
project_number = 502009289245
cloud_region = "us-central1"
zone_id = "b"
topic_id = "tz-lite-topic-oct"
subscription_id = "tz-lite-subscription-oct"
num_messages = 10

location = CloudZone(CloudRegion(cloud_region), zone_id)
topic_path = TopicPath(project_number, location, topic_id)
batch_setttings = BatchSettings(
        # 2 MiB. Default to 3 MiB. Must be less than 4 MiB gRPC's per-message limit.
        max_bytes=2 * 1024 * 1024,
        # 100 ms. Default to 50 ms.
        max_latency=0.1,
        # Default to 1000.
        max_messages=100,
    )

with PublisherClient(per_partition_batching_settings=batch_setttings) as publisher_client:
    future = publisher_client.publish(topic_path, b"hello")
    metadata = future.result()
    x = PublishMetadata.decode(metadata)
    print(x.partition.value)
    print(x.cursor.offset)


subscription_path = SubscriptionPath(project_number, location, subscription_id)
flow_control_settings = FlowControlSettings(
    messages_outstanding=1000, bytes_outstanding=10 * 1024 * 1024
)

def callback(message):
    message_data = message.data.decode("utf-8")
    print(f"Received {message_data} of ordering key {message.ordering_key}.")
    message.ack()

subscriber_client = SubscriberClient()

streaming_pull_future = subscriber_client.subscribe(
    subscription_path,
    callback=callback,
    per_partition_flow_control_settings=flow_control_settings,
)

print(f"Listening for messages on {str(subscription_path)}...")

try:
    streaming_pull_future.result(timeout=65)
except TimeoutError or KeyboardInterrupt:
    streaming_pull_future.cancel()
    assert streaming_pull_future.done()
