#!/usr/bin/env python

# Copyright 2020 Google LLC
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

# [START pubsublite_quickstart_sub_all]
import argparse

# [START pubsublite_quickstart_sub_deps]
from google.cloud.pubsublite.cloudpubsub.flow_control_settings import FlowControlSettings
from google.cloud.pubsublite.cloudpubsub.make_subscriber import make_subscriber
from google.cloud.pubsublite.location import CloudZone
from google.cloud.pubsublite.paths import SubscriptionPath

# [END pubsublite_quickstart_sub_deps]


def sub(project_number: int, location: CloudZone, subscription_id: str):
    """Receives messages from a Pub/Sub subscription."""
    # Create a SubscriptionPath
    subscription_path = SubscriptionPath(project_number, location, subscription_id)

    def callback(message):
        print(
            "Received message {} of message ID {}\n".format(message, message.message_id)
        )
        # Acknowledge the message. Unack'ed messages will be redelivered.
        message.ack()
        print("Acknowledged message {}\n".format(message.message_id))

    # [START pubsublite_quickstart_sub_client]
    # Initialize a Subscriber client
    streaming_pull_future = make_subscriber(
      subscription_path,
      per_partition_flow_control_settings=FlowControlSettings(messages_outstanding=1000, bytes_outstanding=10000000),
      callback=callback
    )
    # [END pubsublite_quickstart_sub_client]
    print("Listening for messages on {}..\n".format(subscription_path))

    try:
        # Calling result() on StreamingPullFuture keeps the main thread from
        # exiting while messages get processed in the callbacks.
        streaming_pull_future.result()
    except:  # noqa
        streaming_pull_future.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Google Cloud project number", type=int)
    parser.add_argument("location", help="Google Cloud zone where the topic is located", type=CloudZone.parse)
    parser.add_argument("subscription_id", help="Pub/Sub subscription ID")

    args = parser.parse_args()

    sub(args.project_number, args.location, args.subscription_id)
# [END pubsublite_quickstart_sub_all]
