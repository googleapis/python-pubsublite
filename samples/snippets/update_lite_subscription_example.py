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

"""This application demonstrates how to update a subscription with the Pub/Sub
Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/subscriptions.
"""

import argparse


def update_lite_subscription(project_number, cloud_region, zone_id, subscription_id):
    # [START pubsublite_update_subscription]
    from google.api_core.exceptions import NotFound
    from google.cloud.pubsublite import AdminClient, Subscription
    from google.cloud.pubsublite.types import CloudRegion, CloudZone, SubscriptionPath
    from google.protobuf.field_mask_pb2 import FieldMask

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # topic_id = "your-topic-id"
    # subscription_id = "your-subscription-id"

    cloud_region = CloudRegion(cloud_region)
    location = CloudZone(cloud_region, zone_id)
    subscription_path = SubscriptionPath(project_number, location, subscription_id)
    field_mask = FieldMask(paths=["delivery_config.delivery_requirement"])

    subscription = Subscription(
        name=str(subscription_path),
        delivery_config=Subscription.DeliveryConfig(
            # Possible values for delivery_requirement:
            # - `DELIVER_IMMEDIATELY`
            # - `DELIVER_AFTER_STORED`
            # `DELIVER_AFTER_STORED` requires a published message to be successfully written
            # to storage before the server delivers it to subscribers.
            delivery_requirement=Subscription.DeliveryConfig.DeliveryRequirement.DELIVER_AFTER_STORED,
        ),
    )

    client = AdminClient(cloud_region)
    try:
        response = client.update_subscription(subscription, field_mask)
        print(f"{response.name} updated successfully.")
    except NotFound:
        print(f"{subscription_path} not found.")
    # [END pubsublite_update_subscription]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("subscription_id", help="Your subscription ID")

    args = parser.parse_args()

    update_lite_subscription(
        args.project_number, args.cloud_region, args.zone_id, args.subscription_id,
    )
