#!/usr/bin/env python

# Copyright 2020 Google Inc. All Rights Reserved.
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

"""This application demonstrates how to publish messages with batch settings with
the Pub/Sub Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/publishing.
"""

import argparse


def publish_with_batch_settings(
    project_number, cloud_region, zone_id, topic_id, num_messages
):
    # [START pubsublite_publish_ordering_key]
    from google.cloud.pubsub_v1.types import BatchSettings
    from google.cloud.pubsublite.cloudpubsub import PublisherClient
    from google.cloud.pubsublite.types import (
        CloudRegion,
        CloudZone,
        PublishMetadata,
        TopicPath,
    )

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # topic_id = "your-topic-id"
    # num_messages = 100

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

    # PublisherClient() must be used in a `with` block or have __enter__() called before use.
    with PublisherClient(
        per_partition_batching_settings=batch_setttings
    ) as publisher_client:
        for message in range(num_messages):
            data = f"{message}"
            api_future = publisher_client.publish(topic_path, data.encode("utf-8"))
            # result() blocks. To resolve API futures asynchronously, use add_done_callback().
            message_id = api_future.result()
            publish_metadata = PublishMetadata.decode(message_id)
            print(
                f"Published {data} to partition {publish_metadata.partition.value} and offset {publish_metadata.cursor.offset}."
            )

    print(
        f"Finished publishing {num_messages} messages with batch settings to {str(topic_path)}."
    )
    # [END pubsublite_publish_ordering_key]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("topic_id", help="Your topic ID")
    parser.add_argument("num_messages", type=int, help="Number of messages to publish")

    args = parser.parse_args()

    publish_with_batch_settings(
        args.project_number,
        args.cloud_region,
        args.zone_id,
        args.topic_id,
        args.num_messages,
    )
