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

"""This application demonstrates how to get a reservation using the
Pub/Sub Lite API. For more information, see the root level README.md and
the documentation at https://cloud.google.com/pubsub/lite/docs/reservations.
"""

import argparse


def get_lite_reservation(project_number, cloud_region, reservation_id):
    # [START pubsublite_get_reservation]
    from google.api_core.exceptions import NotFound
    from google.cloud.pubsublite import AdminClient
    from google.cloud.pubsublite.types import CloudRegion, ReservationPath

    # TODO(developer):
    # project_number = 1122334455
    # cloud_region = "us-central1"
    # reservation_id = "your-reservation-id"

    cloud_region = CloudRegion(cloud_region)
    reservation_path = ReservationPath(project_number, cloud_region, reservation_id)

    client = AdminClient(cloud_region)
    try:
        response = client.get_reservation(reservation_path)
        print(
            f"{response.name} has {response.throughput_capacity} units of throughput capacity."
        )
    except NotFound:
        print(f"{reservation_path} is not found.")
    # [END pubsublite_get_reservation]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Your Google Cloud Project Number")
    parser.add_argument("cloud_region", help="Your Cloud Region, e.g. 'us-central1'")
    parser.add_argument("reservation_id", help="Your reservation ID")

    args = parser.parse_args()

    get_lite_reservation(
        args.project_number, args.cloud_region, args.reservation_id,
    )
