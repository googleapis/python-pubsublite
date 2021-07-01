#!/usr/bin/env python

# Copyright 2021 Google Inc. All Rights Reserved.
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

"""This application demonstrates how to invoke an out-of-band seek for a
subscription with the Pub/Sub Lite API.
"""

import argparse


def seek_lite_subscription(project_number, cloud_region, zone_id, subscription_id, target, wait_for_operation):
    # [START pubsublite_seek_subscription]
    from datetime import datetime
    from google.api_core.exceptions import NotFound, GoogleAPICallError
    from google.cloud.pubsublite import AdminClient
    from google.cloud.pubsublite.types import CloudRegion, CloudZone, SubscriptionPath, BacklogLocation, PublishTime

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # subscription_id = "your-subscription-id"
    # target = "BEGINNING"
    # wait_for_operation = 1

    cloud_region = CloudRegion(cloud_region)
    location = CloudZone(cloud_region, zone_id)
    subscription_path = SubscriptionPath(project_number, location, subscription_id)

    if target == "BEGINNING":
        seek_target = BacklogLocation.BEGINNING
    elif target == "END":
        seek_target = BacklogLocation.END
    else:
        seek_target = PublishTime(datetime.strptime(target, "%Y-%m-%d %H:%M:%S"))

    client = AdminClient(cloud_region)
    try:
        seek_operation = client.seek_subscription(subscription_path, seek_target)
        print(f"Seek operation: {seek_operation.operation.name}")
        print(f"Metadata:\n{seek_operation.metadata}")
    except NotFound:
        print(f"{subscription_path} not found.")

    # Note: In order for the operation to complete, a subscriber must be
    # receiving messages for the subscription.
    if wait_for_operation:
        print("Waiting for operation to complete...")
        try:
            seek_operation.result()
            print(f"Operation completed. Metadata:\n{seek_operation.metadata}")
        except GoogleAPICallError as e:
            print(e)
    # [END pubsublite_seek_subscription]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("subscription_id", help="Your subscription ID")
    parser.add_argument("--target", default="BEGINNING", help="Seek target, e.g. 'BEGINNING, 'END' or a timestamp")
    parser.add_argument("--wait_for_operation", help="Wait for the seek operation to complete")

    args = parser.parse_args()

    seek_lite_subscription(
        args.project_number, args.cloud_region, args.zone_id, args.subscription_id, args.target, args.wait_for_operation
    )
