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

"""This application demonstrates how to update a topic with the Pub/Sub
Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/topics.
"""

import argparse


def update_lite_topic(project_number, cloud_region, zone_id, topic_id):
    # [START pubsublite_update_topic]
    from google.api_core.exceptions import NotFound
    from google.cloud.pubsublite import AdminClient, Topic
    from google.cloud.pubsublite.types import CloudRegion, CloudZone, TopicPath
    from google.protobuf.duration_pb2 import Duration
    from google.protobuf.field_mask_pb2 import FieldMask

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # topic_id = "your-topic-id"

    cloud_region = CloudRegion(cloud_region)
    location = CloudZone(cloud_region, zone_id)
    topic_path = TopicPath(project_number, location, topic_id)

    # Defines which topic fields to update.
    field_mask = FieldMask(
        paths=[
            "partition_config.scale",
            "retention_config.per_partition_bytes",
            "retention_config.period",
        ]
    )

    # Defines how to update the topic fields.
    topic = Topic(
        name=str(topic_path),
        partition_config=Topic.PartitionConfig(
            # Set publishing throughput to 2x standard partition throughput of 4 MiB
            # per second. This must in the range [1,4]. A topic with `scale` of 2 and
            # `count` of 10 is charged for 20 partitions.
            scale=2,
        ),
        retention_config=Topic.RetentionConfig(
            # Set storage per partition to 100 GiB. This must be in the range 30 GiB-10TiB.
            # If the number of byptes stored in any of the topic's partitions grows beyond
            # this value, older messages will be dropped to make room for newer ones,
            # regardless of the value of `period`.
            # Be careful when decreasing storage per partition as it may cuase lost messages.
            per_partition_bytes=100 * 1024 * 1024 * 1024,
            # Allow messages to be stored for 14 days.
            period=Duration(seconds=60 * 60 * 24 * 14),
        ),
    )

    client = AdminClient(cloud_region)
    try:
        response = client.update_topic(topic, field_mask)
        print(f"{response.name} updated successfully.")
    except NotFound:
        print(f"{topic_path} not found.")
    # [END pubsublite_update_topic]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("topic_id", help="Your topic ID")

    args = parser.parse_args()

    update_lite_topic(
        args.project_number, args.cloud_region, args.zone_id, args.topic_id,
    )
