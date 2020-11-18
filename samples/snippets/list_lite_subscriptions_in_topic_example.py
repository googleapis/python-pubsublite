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

"""This application demonstrates how to list subscriptions in your topic with
the Pub/Sub Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/subscriptions.
"""

import argparse


def list_lite_subscriptions_in_topic(project_number, cloud_region, zone_id, topic_id):
    # [START pubsublite_list_subscriptions_in_topic]
    from google.cloud.pubsublite import AdminClient
    from google.cloud.pubsublite.types import CloudRegion, CloudZone, TopicPath

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # topic_id = "your-topic-id"

    cloud_region = CloudRegion(cloud_region)
    location = CloudZone(cloud_region, zone_id)
    topic_path = TopicPath(project_number, location, topic_id)

    client = AdminClient(cloud_region)
    response = client.list_topic_subscriptions(topic_path)

    for subscription_path in response:
        print(subscription_path)

    print(f"{len(response)} subscription(s) listed in your topic.")
    # [END pubsublite_list_subscriptions_in_topic]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("topic_id", help="Your topic ID")

    args = parser.parse_args()

    list_lite_subscriptions_in_topic(
        args.project_number, args.cloud_region, args.zone_id, args.topic_id,
    )
