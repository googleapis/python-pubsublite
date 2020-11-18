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

from abc import ABC, abstractmethod

from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub.message_transforms import (
    to_cps_subscribe_message,
)
from google.cloud.pubsublite_v1 import SequencedMessage


class MessageTransformer(ABC):
    """
  A MessageTransformer turns Pub/Sub Lite message protos into Pub/Sub message protos.
  """

    @abstractmethod
    def transform(self, source: SequencedMessage) -> PubsubMessage:
        """Transform a SequencedMessage to a PubsubMessage.

    Args:
      source: The message to transform.

    Raises:
      GoogleAPICallError: To fail the client if raised inline.
    """
        pass


class DefaultMessageTransformer(MessageTransformer):
    def transform(self, source: SequencedMessage) -> PubsubMessage:
        return to_cps_subscribe_message(source)
