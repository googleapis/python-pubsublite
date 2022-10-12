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

# [START pubsublite_create_pubsub_export_subscription]
from google.api_core.exceptions import AlreadyExists
from google.cloud.pubsub_v1 import PublisherClient
from google.cloud.pubsublite import AdminClient, Subscription, ExportConfig
from google.cloud.pubsublite.types import (
    BacklogLocation,
    CloudRegion,
    CloudZone,
    SubscriptionPath,
    TopicPath,
)


def create_lite_pubsub_export_subscription(
    project_number,
    cloud_region="us-central1",
    zone_id="a",
    topic_id="my-topic-id",
    subscription_id="my-subscription-id",
    pubsub_topic_id="destination-topic-id",
    regional=True,
    target_location=BacklogLocation.END,
):
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

    # Initialize client that will be used to send requests across threads. This
    # client only needs to be created once, and can be reused for multiple requests.
    client = AdminClient(cloud_region)
    try:
        response = client.create_subscription(subscription, target_location)
        print(f"{response.name} created successfully.")
    except AlreadyExists:
        print(f"{subscription_path} already exists.")

# [END pubsublite_create_pubsub_export_subscription]
