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
from typing import List

from google.cloud.pubsublite.types import (
    CloudRegion,
    TopicPath,
    LocationPath,
    SubscriptionPath,
    OffsetLocation,
)
from google.cloud.pubsublite_v1 import Topic, Subscription
from google.protobuf.field_mask_pb2 import FieldMask


class AdminClientInterface(ABC):
    """
    An admin client for Pub/Sub Lite. Only operates on a single region.
    """

    @abstractmethod
    def region(self) -> CloudRegion:
        """The region this client is for."""

    @abstractmethod
    def create_topic(self, topic: Topic) -> Topic:
        """Create a topic, returns the created topic."""

    @abstractmethod
    def get_topic(self, topic_path: TopicPath) -> Topic:
        """Get the topic object from the server."""

    @abstractmethod
    def get_topic_partition_count(self, topic_path: TopicPath) -> int:
        """Get the number of partitions in the provided topic."""

    @abstractmethod
    def list_topics(self, location_path: LocationPath) -> List[Topic]:
        """List the Pub/Sub lite topics that exist for a project in a given location."""

    @abstractmethod
    def update_topic(self, topic: Topic, update_mask: FieldMask) -> Topic:
        """Update the masked fields of the provided topic."""

    @abstractmethod
    def delete_topic(self, topic_path: TopicPath):
        """Delete a topic and all associated messages."""

    @abstractmethod
    def list_topic_subscriptions(self, topic_path: TopicPath):
        """List the subscriptions that exist for a given topic."""

    @abstractmethod
    def create_subscription(self, subscription: Subscription) -> Subscription:
        """Create a subscription, returns the created subscription."""

    @abstractmethod
    def create_subscription_at_offset(
        self, subscription: Subscription, starting_offset: OffsetLocation
    ) -> Subscription:
        """Create a subscription at the given starting offset, returns the created subscription."""

    @abstractmethod
    def get_subscription(self, subscription_path: SubscriptionPath) -> Subscription:
        """Get the subscription object from the server."""

    @abstractmethod
    def list_subscriptions(self, location_path: LocationPath) -> List[Subscription]:
        """List the Pub/Sub lite subscriptions that exist for a project in a given location."""

    @abstractmethod
    def update_subscription(
        self, subscription: Subscription, update_mask: FieldMask
    ) -> Subscription:
        """Update the masked fields of the provided subscription."""

    @abstractmethod
    def delete_subscription(self, subscription_path: SubscriptionPath):
        """Delete a subscription and all associated messages."""
