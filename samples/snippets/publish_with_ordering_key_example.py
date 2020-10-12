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

"""This application demonstrates how to publish messages with an ordering key with
the Pub/Sub Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/publishing.
"""

import argparse


def publish_with_odering_key(
    project_number, cloud_region, zone_id, topic_id, num_messages
):
    # [START pubsublite_publish_ordering_key]
    from google.cloud.pubsublite.cloudpubsub.make_publisher import make_publisher
    from google.cloud.pubsublite.location import CloudRegion, CloudZone
    from google.cloud.pubsublite.paths import TopicPath
    from google.cloud.pubsublite.publish_metadata import PublishMetadata

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # toic_id = "your-topic-id"
    # num_messages = 100

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    topic_path = TopicPath(project_number, location, topic_id)

    with make_publisher(topic_path) as publisher_client:
        for message in range(num_messages):
            data = f"{message}"
            # Messages of the same ordering key will always get published to the same partition.
            # When ordering_key is unset, messsages can get published ot different partitions if
            # more than one partition exists for the topic.
            api_future = publisher_client.publish(
                data.encode("utf-8"), ordering_key="testing"
            )
            # result() blocks. To resolve api futures asynchronously, use add_done_callback().
            ack_id = api_future.result()
            publish_metadata = PublishMetadata.decode(ack_id)
            print(
                f"Published {data} to partition {publish_metadata.partition.value} and offset {publish_metadata.cursor.offset}."
            )

    print(f"Finished publishing {num_messages} messages with an ordering key.")
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

    publish_with_odering_key(
        args.project_number,
        args.cloud_region,
        args.zone_id,
        args.topic_id,
        args.num_messages,
    )
