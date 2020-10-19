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

"""This application demonstrates how to receive messages with the
Pub/Sub Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/subscribing.
"""

import argparse


def receive_messages(project_number, cloud_region, zone_id, subscription_id, timeout=90):
    # [START pubsublite_quickstart_subscriber]
    from concurrent.futures._base import TimeoutError
    from google.cloud.pubsublite.cloudpubsub.flow_control_settings import FlowControlSettings
    from google.cloud.pubsublite.cloudpubsub.make_subscriber import make_subscriber
    from google.cloud.pubsublite.location import CloudRegion, CloudZone
    from google.cloud.pubsublite.paths import SubscriptionPath

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # subscription_id = "your-subscription-id"
    # timeout = 90

    location = CloudZone(CloudRegion(cloud_region), zone_id)
    subscription_path = SubscriptionPath(project_number, location, subscription_id)
    flow_control_settings = FlowControlSettings(
        messages_outstanding=1000, bytes_outstanding=10 * 1024 * 1024
    )

    def callback(message):
        message_data = message.data.decode("utf-8")
        print(f"Received {message_data} of ordering key {message.ordering_key}.")
        message.ack()

    streaming_pull_future = make_subscriber(
        subscription_path,
        per_partition_flow_control_settings=flow_control_settings,
        callback=callback,
    )

    print(f"Listening for messages on {str(subscription_path)}...")

    try:
        streaming_pull_future.result(timeout=timeout)
    except TimeoutError or KeyboardInterrupt:
        streaming_pull_future.cancel()
        assert streaming_pull_future.done()
    # [END pubsublite_quickstart_subscriber]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("subscription_id", help="Your subscription ID")
    parser.add_argument(
        "timeout", nargs="?", default=90, type=int, help="Timeout in second"
    )

    args = parser.parse_args()

    receive_messages(
        args.project_number,
        args.cloud_region,
        args.zone_id,
        args.subscription_id,
        args.timeout,
    )
