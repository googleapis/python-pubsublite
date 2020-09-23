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

# [START pubsublite_quickstart_pub_all]
import argparse
import time

# [START pubsublite_quickstart_pub_deps]
from google.cloud.pubsublite.cloudpubsub.make_publisher import make_publisher
from google.cloud.pubsublite.location import CloudZone
from google.cloud.pubsublite.paths import TopicPath

# [END pubsublite_quickstart_pub_deps]


def get_callback(data, ref):
    """Wrap message data in the context of the callback function."""

    def callback(api_future):
        try:
            print(
                "Published message {} now has message ID {}".format(
                    data, api_future.result()
                )
            )
            ref["num_messages"] += 1
        except Exception:
            print(
                "A problem occurred when publishing {}: {}\n".format(
                    data, api_future.exception()
                )
            )
            raise

    return callback


def pub(project_number: int, location: CloudZone, topic_id: str):
    """Publishes a message to a Pub/Sub Lite topic."""
    # [START pubsublite_quickstart_pub_client]
    # Initialize a Publisher client.
    with make_publisher(TopicPath(project_number, location, topic_id)) as client:
      # [END pubsublite_quickstart_pub_client]
      # Data sent to Pub/Sub Lite must be a bytestring.
      data = b"Hello, World!"

      # Keep track of the number of published messages.
      ref = dict({"num_messages": 0})

      # When you publish a message, the client returns a future.
      api_future = client.publish(data)
      api_future.add_done_callback(get_callback(data, ref))

      # Keep the main thread from exiting while the message future
      # gets resolved in the background.
      while api_future.running():
          time.sleep(0.5)
          print("Published {} message(s).".format(ref["num_messages"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_number", help="Google Cloud project number", type=int)
    parser.add_argument("location", help="Google Cloud zone where the topic is located", type=CloudZone.parse)
    parser.add_argument("topic_id", help="Pub/Sub topic ID")

    args = parser.parse_args()

    pub(args.project_id, args.location, args.topic_id)
# [END pubsublite_quickstart_pub_all]
