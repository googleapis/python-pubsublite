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

from typing import List

from google.protobuf.field_mask_pb2 import FieldMask

from google.cloud.pubsublite.admin_client_interface import AdminClientInterface
from google.cloud.pubsublite.types import (
    CloudRegion,
    SubscriptionPath,
    LocationPath,
    TopicPath,
    BacklogLocation,
)
from google.cloud.pubsublite_v1 import (
    Subscription,
    Topic,
    AdminServiceClient,
    TopicPartitions,
)


class AdminClientImpl(AdminClientInterface):
    _underlying: AdminServiceClient
    _region: CloudRegion

    def __init__(self, underlying: AdminServiceClient, region: CloudRegion):
        self._underlying = underlying
        self._region = region

    def region(self) -> CloudRegion:
        return self._region

    def create_topic(self, topic: Topic) -> Topic:
        path = TopicPath.parse(topic.name)
        return self._underlying.create_topic(
            parent=str(path.to_location_path()), topic=topic, topic_id=path.name
        )

    def get_topic(self, topic_path: TopicPath) -> Topic:
        return self._underlying.get_topic(name=str(topic_path))

    def get_topic_partition_count(self, topic_path: TopicPath) -> int:
        partitions: TopicPartitions = self._underlying.get_topic_partitions(
            name=str(topic_path)
        )
        return partitions.partition_count

    def list_topics(self, location_path: LocationPath) -> List[Topic]:
        return [x for x in self._underlying.list_topics(parent=str(location_path))]

    def update_topic(self, topic: Topic, update_mask: FieldMask) -> Topic:
        return self._underlying.update_topic(topic=topic, update_mask=update_mask)

    def delete_topic(self, topic_path: TopicPath):
        self._underlying.delete_topic(name=str(topic_path))

    def list_topic_subscriptions(self, topic_path: TopicPath):
        subscription_strings = [
            x for x in self._underlying.list_topic_subscriptions(name=str(topic_path))
        ]
        return [SubscriptionPath.parse(x) for x in subscription_strings]

    def create_subscription(
        self,
        subscription: Subscription,
        starting_offset: BacklogLocation = BacklogLocation.END,
    ) -> Subscription:
        path = SubscriptionPath.parse(subscription.name)
        return self._underlying.create_subscription(
            request={
                "parent": str(path.to_location_path()),
                "subscription": subscription,
                "subscription_id": path.name,
                "skip_backlog": (starting_offset == BacklogLocation.END),
            }
        )

    def get_subscription(self, subscription_path: SubscriptionPath) -> Subscription:
        return self._underlying.get_subscription(name=str(subscription_path))

    def list_subscriptions(self, location_path: LocationPath) -> List[Subscription]:
        return [
            x for x in self._underlying.list_subscriptions(parent=str(location_path))
        ]

    def update_subscription(
        self, subscription: Subscription, update_mask: FieldMask
    ) -> Subscription:
        return self._underlying.update_subscription(
            subscription=subscription, update_mask=update_mask
        )

    def delete_subscription(self, subscription_path: SubscriptionPath):
        self._underlying.delete_subscription(name=str(subscription_path))
