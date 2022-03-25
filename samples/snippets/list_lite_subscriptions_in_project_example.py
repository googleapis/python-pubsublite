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

"""This application demonstrates how to list subscriptions in your project and
location with the Pub/Sub Lite API. For more information, see the root level README.md
and the documentation at https://cloud.google.com/pubsub/lite/docs/subscriptions.
"""

import argparse


def list_lite_subscriptions_in_project(project_number, cloud_region, zone_id, regional):
    # [START pubsublite_list_subscriptions_in_project]
    from google.cloud.pubsublite import AdminClient
    from google.cloud.pubsublite.types import CloudRegion, CloudZone, LocationPath

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # zone_id = "a"
    # regional = True

    if regional:
        location = CloudRegion(cloud_region)
    else:
        location = CloudZone(CloudRegion(cloud_region), zone_id)

    location_path = LocationPath(project_number, location)

    client = AdminClient(cloud_region)
    response = client.list_subscriptions(location_path)

    for subscription in response:
        print(subscription.name)

    print(f"{len(response)} subscription(s) listed in your project and location.")
    # [END pubsublite_list_subscriptions_in_project]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("zone_id", help="Your Zone ID, e.g. 'a'")
    parser.add_argument("regional", help="True if using a regional location else zonal")

    args = parser.parse_args()

    list_lite_subscriptions_in_project(
        args.project_number, args.cloud_region, args.zone_id, args.regional
    )
