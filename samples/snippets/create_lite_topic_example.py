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
    from google.cloud.pubsublite.location import CloudRegion, CloudZone
    from google.cloud.pubsublite.make_admin_client import make_admin_client
    from google.cloud.pubsublite.paths import TopicPath
    from google.cloud.pubsublite_v1 import Topic
    from google.protobuf.duration_pb2 import Duration

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # toic_id = "your-topic-id"
    # num_partitions = 1

    client = make_admin_client(cloud_region)

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    topic_path = str(TopicPath(project_number, location, topic_id))
    topic = Topic(
        name=topic_path,
        partition_config=Topic.PartitionConfig(
            # This must be greater than 1.
            count=num_partitions,
            # Set publishing throughput to 1x standard partition throughput of 4 MiB
            # per second. This must in the range [1,4]. A topic with `scale` of 2 and
            # `count` of 10 is charged for 20 partitions.
            scale=1,
        ),
        retention_config=Topic.RetentionConfig(
            # Set storage per partition to 30 GiB. This must be in the range 30 GiB-10TiB.
            # If the number of byptes stored in any of the topic's partitions grows beyond
            # this value, older messages will be dropped to make room for newer ones,
            # regardless of the value of `period`.
            per_partition_bytes=30 * 1024 * 1024 * 1024,
            # How long messages are retained.
            period=Duration(seconds=60 * 60 * 24 * 7),
        ),
    )

    response = client.create_topic(topic)
    print(f"{response}\ncreated successfully.")
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