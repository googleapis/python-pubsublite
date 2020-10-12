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

"""This application demonstrates how to create a subscription with the Pub/Sub
Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/subscriptions.
"""

import argparse


def create_lite_subscription(
    project_number, cloud_region, zone_id, topic_id, subscription_id
):
    # [START pubsublite_create_subscription]
    from google.cloud.pubsublite.location import CloudRegion, CloudZone
    from google.cloud.pubsublite.make_admin_client import make_admin_client
    from google.cloud.pubsublite.paths import SubscriptionPath, TopicPath
    from google.cloud.pubsublite_v1 import Subscription

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # topic_id = "your-topic-id"
    # subscription_id = "your-subscription-id"

    client = make_admin_client(cloud_region)

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    topic_path = str(TopicPath(project_number, location, topic_id))
    subscription_path = str(SubscriptionPath(project_number, location, subscription_id))

    subscription = Subscription(
        name=subscription_path,
        topic=topic_path,
        delivery_config=Subscription.DeliveryConfig(
            # The server does not wait for a published message to be successfully
            # written to storage before delivering it to subscribers. As such, a subscriber
            # may receive a message for which the write to storage failed. If the subscriber
            # re-reads the offset of that mesage later on, there may be a gap at that offset.
            delivery_requirement=Subscription.DeliveryConfig.DeliveryRequirement.DELIVER_IMMEDIATELY,
        ),
    )

    response = client.create_subscription(subscription)
    print(f"{response}\ncreated successfully.")
    # [END pubsublite_create_subscription]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("topic_id", help="Your topic ID")
    parser.add_argument("subscription_id", help="Your subscription ID")

    args = parser.parse_args()

    create_lite_subscription(
        args.project_number,
        args.cloud_region,
        args.zone_id,
        args.topic_id,
        args.subscription_id,
    )
