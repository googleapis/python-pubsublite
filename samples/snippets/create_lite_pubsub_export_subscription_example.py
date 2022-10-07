#!/usr/bin/env python

# Copyright 2022 Google Inc. All Rights Reserved.
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

"""This application demonstrates how to create a subscription that writes
messages to a Pub/Sub topic. For more information, see documentation at
https://cloud.google.com/pubsub/lite/docs/export-subscriptions.
"""

import argparse


def create_lite_pubsub_export_subscription(
    project_number,
    cloud_region,
    zone_id,
    topic_id,
    subscription_id,
    pubsub_topic_id,
    regional,
    target_location,
):
    # [START pubsublite_create_pubsub_export_subscription]
    from google.api_core.exceptions import AlreadyExists
    from google.cloud.pubsub_v1 import PublisherClient
    from google.cloud.pubsublite import AdminClient, Subscription, ExportConfig
    from google.cloud.pubsublite.types import (
        CloudRegion,
        CloudZone,
        SubscriptionPath,
        TopicPath,
    )

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # topic_id = "your-topic-id"
    # subscription_id = "your-subscription-id"
    # pubsub_topic_id = "destination-topic-id"
    # regional = True
    # target_location = BacklogLocation.BEGINNING

    if regional:
        location = CloudRegion(cloud_region)
    else:
        location = CloudZone(CloudRegion(cloud_region), zone_id)

    topic_path = TopicPath(project_number, location, topic_id)
    subscription_path = SubscriptionPath(project_number, location, subscription_id)
    destination_topic_path = PublisherClient.topic_path(project_number, pubsub_topic_id)

    subscription = Subscription(
        name=str(subscription_path),
        topic=str(topic_path),
        delivery_config=Subscription.DeliveryConfig(
            # Possible values for delivery_requirement:
            # - `DELIVER_IMMEDIATELY`
            # - `DELIVER_AFTER_STORED`
            # You may choose whether to wait for a published message to be successfully written
            # to storage before the server delivers it to subscribers. `DELIVER_IMMEDIATELY` is
            # suitable for applications that need higher throughput.
            delivery_requirement=Subscription.DeliveryConfig.DeliveryRequirement.DELIVER_IMMEDIATELY,
        ),
        export_config=ExportConfig(
            # Possible values for desired_state:
            # - `ACTIVE`: enable message processing.
            # - `PAUSED`: suspend message processing.
            desired_state=ExportConfig.State.ACTIVE,
            pubsub_config=ExportConfig.PubSubConfig(
                topic=destination_topic_path,
            ),
        ),
    )

    client = AdminClient(cloud_region)
    try:
        response = client.create_subscription(subscription, target_location)
        print(f"{response.name} created successfully.")
    except AlreadyExists:
        print(f"{subscription_path} already exists.")
    # [END pubsublite_create_pubsub_export_subscription]


if __name__ == "__main__":
    from datetime import datetime
    from google.cloud.pubsublite.types import BacklogLocation, PublishTime

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("topic_id", help="Your Lite topic ID")
    parser.add_argument("subscription_id", help="Your Lite subscription ID")
    parser.add_argument("pubsub_topic_id", help="The destination Pub/Sub topic ID")
    parser.add_argument(
        "--regional",
        default=False,
        help="True if the Lite resource is regional else zonal",
    )
    parser.add_argument(
        "--target",
        default="BEGINNING",
        help="Initial location in the message backlog, e.g. 'BEGINNING, 'END' or a timestamp",
    )

    args = parser.parse_args()

    if args.target == "BEGINNING":
        target_location = BacklogLocation.BEGINNING
    elif args.target == "END":
        target_location = BacklogLocation.END
    else:
        target_location = PublishTime(
            datetime.strptime(args.target, "%Y-%m-%d %H:%M:%S")
        )

    create_lite_pubsub_export_subscription(
        args.project_number,
        args.cloud_region,
        args.zone_id,
        args.topic_id,
        args.subscription_id,
        args.pubsub_topic_id,
        args.regional,
        target_location,
    )
