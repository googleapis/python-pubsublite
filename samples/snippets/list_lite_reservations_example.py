#!/usr/bin/env python

# Copyright 2022 Google LLC. All Rights Reserved.
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

"""This application demonstrates how to list reservations using the Pub/Sub
Lite API. For more information, see the root level README.md and the
documentation at https://cloud.google.com/pubsub/lite/docs/topics.
"""

import argparse


def list_lite_reservations(project_number, cloud_region):
    # [START pubsublite_list_reservations]
    from google.cloud.pubsublite import AdminClient
    from google.cloud.pubsublite.types import LocationPath

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"

    location_path = LocationPath(project_number, cloud_region)

    client = AdminClient(cloud_region)
    response = client.list_reservations(location_path)

    for reservation in response:
        print(reservation)

    print(f"{len(response)} reservation(s) listed in your project and location.")
    # [END pubsublite_list_reservations]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")

    args = parser.parse_args()

    list_lite_reservations(args.project_number, args.cloud_region)
