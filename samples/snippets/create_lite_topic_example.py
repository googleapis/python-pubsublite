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

"""This application demonstrates how to create a topic with the Pub/Sub
Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/topics.
"""

import argparse


def create_lite_topic(project_number, cloud_region, zone_id, topic_id, num_partitions):
    # [START pubsublite_create_topic]
    from google.api_core.exceptions import AlreadyExists
    from google.cloud.pubsublite import AdminClient, Topic
    from google.cloud.pubsublite.types import CloudRegion, CloudZone, TopicPath
    from google.protobuf.duration_pb2 import Duration

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # topic_id = "your-topic-id"
    # num_partitions = 1

    cloud_region = CloudRegion(cloud_region)
    location = CloudZone(cloud_region, zone_id)
    topic_path = TopicPath(project_number, location, topic_id)
    topic = Topic(
        name=str(topic_path),
        partition_config=Topic.PartitionConfig(
            # A topic must have at least one partition.
            count=num_partitions,
            # Set throughput capacity per partition in MiB/s.
            capacity=Topic.PartitionConfig.Capacity(
                # Set publish throughput capacity per partition to 4 MiB/s. Must be >= 4 and <= 16.
                publish_mib_per_sec=4,
                # Set subscribe throughput capacity per partition to 4 MiB/s. Must be >= 4 and <= 32.
                subscribe_mib_per_sec=8,
            ),
        ),
        retention_config=Topic.RetentionConfig(
            # Set storage per partition to 30 GiB. This must be in the range 30 GiB-10TiB.
            # If the number of byptes stored in any of the topic's partitions grows beyond
            # this value, older messages will be dropped to make room for newer ones,
            # regardless of the value of `period`.
            per_partition_bytes=30 * 1024 * 1024 * 1024,
            # Allow messages to be retained for 7 days.
            period=Duration(seconds=60 * 60 * 24 * 7),
        ),
    )

    client = AdminClient(cloud_region)
    try:
        response = client.create_topic(topic)
        print(f"{response.name} created successfully.")
    except AlreadyExists:
        print(f"{topic_path} already exists.")
    # [END pubsublite_create_topic]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("topic_id", help="Your topic ID")
    parser.add_argument(
        "num_partitions", type=int, help="Number of partitions in the topic"
    )

    args = parser.parse_args()

    create_lite_topic(
        args.project_number,
        args.cloud_region,
        args.zone_id,
        args.topic_id,
        args.num_partitions,
    )
