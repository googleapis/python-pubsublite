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

"""This application demonstrates how to publish messages with the Pub/Sub
Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/publishing.
"""

import argparse


def publish(project_number, cloud_region, zone_id, topic_id, num_messages):
    # [START pubsublite_quickstart_publisher]
    from google.cloud.pubsublite.location import CloudRegion, CloudZone
    from google.cloud.pubsublite.cloudpubsub.make_publisher import make_publisher
    from google.cloud.pubsublite.paths import TopicPath

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # toic_id = "your-topic-id"
    # num_messages = 100

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    topic_path_object = str(TopicPath(project_number, location, topic_id))

    publisher_client = make_publisher(topic_path_object)

    for message in range(num_messages):
        data = f"{message}"
        api_future = publisher_client.publish(data.encode("utf-8"))
        # result() blocks. You may use add_done_callback() to resolve api futures asynchronously.
        message_id = api_future.result()
        print(f"Published message {message} has message ID {message_id}.")

    print(f"Published {num_messages} messages.")
    # [END pubsublite_quickstart_publisher]


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

    publish(
        args.project_number,
        args.cloud_region,
        args.zone_id,
        args.topic_id,
        args.num_messages,
    )