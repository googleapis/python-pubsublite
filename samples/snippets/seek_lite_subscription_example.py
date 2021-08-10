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

"""This application demonstrates how to initiate an out-of-band seek for a
subscription with the Pub/Sub Lite API. For more information, see the
documentation at https://cloud.google.com/pubsub/lite/docs/seek.
"""

import argparse


def seek_lite_subscription(project_number, cloud_region, zone_id, subscription_id, seek_target, wait_for_operation):
    # [START pubsublite_seek_subscription]
    from google.api_core.exceptions import NotFound
    from google.cloud.pubsublite import AdminClient
    from google.cloud.pubsublite.types import CloudRegion, CloudZone, SubscriptionPath

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # subscription_id = "your-subscription-id"
    # seek_target = BacklogLocation.BEGINNING
    # wait_for_operation = False

    # Possible values for seek_target:
    # - BacklogLocation.BEGINNING: replays from the beginning of all retained
    #   messages.
    # - BacklogLocation.END: skips past all current published messages.
    # - PublishTime(<datetime>): delivers messages with publish time greater
    #   than or equal to the specified timestamp.
    # - EventTime(<datetime>): seeks to the first message with event time
    #   greater than or equal to the specified timestamp.

    # Waiting for the seek operation to complete is optional. It indicates when
    # subscribers for all partitions are receiving messages from the seek
    # target. If subscribers are offline, the operation will complete once they
    # are online.

    cloud_region = CloudRegion(cloud_region)
    location = CloudZone(cloud_region, zone_id)
    subscription_path = SubscriptionPath(project_number, location, subscription_id)

    client = AdminClient(cloud_region)
    try:
        # Initiate an out-of-band seek for a subscription to the specified
        # target. If an operation is returned, the seek has been successfully
        # registered and will eventually propagate to subscribers.
        seek_operation = client.seek_subscription(subscription_path, seek_target)
        print(f"Seek operation: {seek_operation.operation.name}")
    except NotFound:
        print(f"{subscription_path} not found.")
        return

    if wait_for_operation:
        print("Waiting for operation to complete...")
        seek_operation.result()
        print(f"Operation completed. Metadata:\n{seek_operation.metadata}")
    # [END pubsublite_seek_subscription]


if __name__ == "__main__":
    from datetime import datetime
    from google.cloud.pubsublite.types import BacklogLocation, PublishTime

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

    if args.target == "BEGINNING":
        seek_target = BacklogLocation.BEGINNING
    elif args.target == "END":
        seek_target = BacklogLocation.END
    else:
        seek_target = PublishTime(datetime.strptime(args.target, "%Y-%m-%d %H:%M:%S"))

    seek_lite_subscription(
        args.project_number, args.cloud_region, args.zone_id,
        args.subscription_id, seek_target, args.wait_for_operation
    )
