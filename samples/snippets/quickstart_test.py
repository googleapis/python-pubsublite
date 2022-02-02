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

import os
import random
import uuid

import backoff
from google.api_core.exceptions import AlreadyExists, FailedPrecondition, NotFound
from google.cloud.pubsublite import AdminClient, Reservation, Subscription, Topic
from google.cloud.pubsublite.types import (
    BacklogLocation,
    CloudRegion,
    CloudZone,
    ReservationPath,
    SubscriptionPath,
    TopicPath,
)
from google.protobuf.duration_pb2 import Duration
import pytest

PROJECT_NUMBER = os.environ["GOOGLE_CLOUD_PROJECT_NUMBER"]
CLOUD_REGION = "us-central1"
ZONE_ID = ["a", "b", "c"][random.randint(0, 2)]
UUID = uuid.uuid4().hex
TOPIC_ID = "py-lite-topic-" + UUID
SUBSCRIPTION_ID = "py-lite-subscription-" + UUID
RESERVATION_ID = "py-lite-reservation-" + UUID
NUM_PARTITIONS = 1
NUM_MESSAGES = 10
# Allow 90s for tests to finish.
MAX_TIME = 90


@pytest.fixture(scope="module")
def client():
    yield AdminClient(CLOUD_REGION)


@pytest.fixture(scope="module")
def reservation(client):
    """Creates a reservation resource."""
    reservation_path_object = ReservationPath(
        PROJECT_NUMBER, CLOUD_REGION, RESERVATION_ID
    )
    reservation_path = str(reservation_path_object)
    try:
        response = client.create_reservation(
            Reservation(name=reservation_path, throughput_capacity=10,)
        )
    except AlreadyExists:
        response = client.get_reservation(reservation_path)
    yield response
    try:
        client.delete_reservation(response.name)
    except (NotFound, FailedPrecondition):
        print(f"Reservation {response.name} has been cleaned up.")


@pytest.fixture(scope="module")
def zonal_topic(client, reservation):
    """Creates a zonal topic resource."""
    location = CloudZone(CloudRegion(CLOUD_REGION), ZONE_ID)
    zonal_topic_path_object = TopicPath(PROJECT_NUMBER, location, TOPIC_ID)
    zonal_topic_path = str(zonal_topic_path_object)
    reservation_path = reservation.name

    zonal_topic = Topic(
        name=zonal_topic_path,
        partition_config=Topic.PartitionConfig(
            count=NUM_PARTITIONS,
            capacity=Topic.PartitionConfig.Capacity(
                publish_mib_per_sec=4, subscribe_mib_per_sec=8,
            ),
        ),
        retention_config=Topic.RetentionConfig(
            per_partition_bytes=30 * 1024 * 1024 * 1024,
            period=Duration(seconds=60 * 60 * 24 * 7),
        ),
        reservation_config=Topic.ReservationConfig(
            throughput_reservation=reservation_path,
        ),
    )

    try:
        response = client.create_topic(zonal_topic)
    except AlreadyExists:
        response = client.get_topic(zonal_topic_path)

    yield response
    try:
        client.delete_topic(response.name)
    except NotFound:
        print(f"{response.name} (zonal topic) has been cleaned up.")


@pytest.fixture(scope="module")
def regional_topic(client, reservation):
    """Creates a regional topic resource."""
    location = CloudRegion(CLOUD_REGION)
    regional_topic_path_object = TopicPath(PROJECT_NUMBER, location, TOPIC_ID)
    regional_topic_path = str(regional_topic_path_object)
    reservation_path = reservation.name

    regional_topic = Topic(
        name=regional_topic_path,
        partition_config=Topic.PartitionConfig(
            count=NUM_PARTITIONS,
            capacity=Topic.PartitionConfig.Capacity(
                publish_mib_per_sec=4, subscribe_mib_per_sec=8,
            ),
        ),
        retention_config=Topic.RetentionConfig(
            per_partition_bytes=30 * 1024 * 1024 * 1024,
            period=Duration(seconds=60 * 60 * 24 * 7),
        ),
        reservation_config=Topic.ReservationConfig(
            throughput_reservation=reservation_path,
        ),
    )

    try:
        response = client.create_topic(regional_topic)
    except AlreadyExists:
        response = client.get_topic(regional_topic_path)

    yield response
    try:
        client.delete_topic(response.name)
    except NotFound:
        print(f"{response.name} (regional topic) has been cleaned up.")


@pytest.fixture(scope="module")
def subscription(client, zonal_topic):
    """Creates a subscription resource"""
    location = CloudZone(CloudRegion(CLOUD_REGION), ZONE_ID)
    subscription_path_object = SubscriptionPath(
        PROJECT_NUMBER, location, SUBSCRIPTION_ID
    )
    subscription_path = str(subscription_path_object)
    zonal_topic_path = zonal_topic.name
    subscription = Subscription(
        name=subscription_path,
        topic=zonal_topic_path,
        delivery_config=Subscription.DeliveryConfig(
            delivery_requirement=Subscription.DeliveryConfig.DeliveryRequirement.DELIVER_IMMEDIATELY,
        ),
    )

    try:
        response = client.create_subscription(subscription)
    except AlreadyExists:
        response = client.get_subscription(subscription_path)

    yield response
    try:
        client.delete_subscription(response.name)
    except NotFound:
        print(f"Subscription {response.name} has been cleaned up.")


def test_create_lite_topic_example(reservation, capsys):
    import create_lite_topic_example

    reservation_path_object = ReservationPath.parse(reservation.name)

    wanted_regional_topic_path = (
        f"projects/{PROJECT_NUMBER}/locations/{CLOUD_REGION}/topics/{TOPIC_ID}"
    )
    wanted_zonal_topic_path = f"projects/{PROJECT_NUMBER}/locations/{CLOUD_REGION}-{ZONE_ID}/topics/{TOPIC_ID}"

    create_lite_topic_example.create_lite_topic(
        PROJECT_NUMBER,
        CLOUD_REGION,
        ZONE_ID,
        TOPIC_ID,
        reservation_path_object.name,
        NUM_PARTITIONS,
        True,
    )

    create_lite_topic_example.create_lite_topic(
        PROJECT_NUMBER,
        CLOUD_REGION,
        ZONE_ID,
        TOPIC_ID,
        reservation_path_object.name,
        NUM_PARTITIONS,
        False,
    )

    out, _ = capsys.readouterr()

    assert f"{wanted_regional_topic_path} (regional topic) created successfully." in out
    assert f"{wanted_zonal_topic_path} (zonal topic) created successfully." in out


def test_update_lite_topic_example(zonal_topic, regional_topic, reservation, capsys):
    import update_lite_topic_example

    reservation_path_object = ReservationPath.parse(reservation.name)

    update_lite_topic_example.update_lite_topic(
        PROJECT_NUMBER,
        CLOUD_REGION,
        ZONE_ID,
        TOPIC_ID,
        reservation_path_object.name,
        True,
    )

    update_lite_topic_example.update_lite_topic(
        PROJECT_NUMBER,
        CLOUD_REGION,
        ZONE_ID,
        TOPIC_ID,
        reservation_path_object.name,
        False,
    )
    out, _ = capsys.readouterr()
    assert f"{zonal_topic.name} updated successfully." in out
    assert f"{regional_topic.name} updated successfully." in out


def test_get_lite_topic_example(zonal_topic, regional_topic, capsys):
    import get_lite_topic_example

    get_lite_topic_example.get_lite_topic(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, True
    )

    get_lite_topic_example.get_lite_topic(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, False
    )
    out, _ = capsys.readouterr()
    assert f"{zonal_topic.name} has {NUM_PARTITIONS} partition(s)." in out
    assert f"{regional_topic.name} has {NUM_PARTITIONS} partition(s)." in out


def test_list_lite_topics_example(zonal_topic, regional_topic, capsys):
    import list_lite_topics_example

    # List regional topics
    list_lite_topics_example.list_lite_topics(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, True,
    )
    # List zonal topics
    list_lite_topics_example.list_lite_topics(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, False,
    )
    out, _ = capsys.readouterr()
    assert f"{zonal_topic.name}"
    assert f"{regional_topic.name}"
    assert "topic(s) listed in your project and location." in out


def test_create_lite_subscription(capsys):
    import create_lite_subscription_example

    wanted_subscription_path = f"projects/{PROJECT_NUMBER}/locations/{CLOUD_REGION}-{ZONE_ID}/subscriptions/{SUBSCRIPTION_ID}"

    create_lite_subscription_example.create_lite_subscription(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, SUBSCRIPTION_ID,
    )
    out, _ = capsys.readouterr()
    assert f"{wanted_subscription_path} created successfully." in out


def test_update_lite_subscription_example(subscription, capsys):
    import update_lite_subscription_example

    update_lite_subscription_example.update_lite_subscription(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, SUBSCRIPTION_ID,
    )
    out, _ = capsys.readouterr()
    assert f"{subscription.name} updated successfully." in out


def test_get_lite_subscription(subscription, capsys):
    import get_lite_subscription_example

    get_lite_subscription_example.get_lite_subscription(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, SUBSCRIPTION_ID,
    )
    out, _ = capsys.readouterr()
    assert f"{subscription.name} exists." in out


def test_list_lite_subscriptions_in_project(subscription, capsys):
    import list_lite_subscriptions_in_project_example

    list_lite_subscriptions_in_project_example.list_lite_subscriptions_in_project(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID,
    )
    out, _ = capsys.readouterr()
    assert f"{subscription.name}" in out
    assert "subscription(s) listed in your project and location." in out


def test_list_lite_subscriptions_in_topic(subscription, capsys):
    import list_lite_subscriptions_in_topic_example

    list_lite_subscriptions_in_topic_example.list_lite_subscriptions_in_topic(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID,
    )
    out, _ = capsys.readouterr()
    assert f"{subscription.name}" in out
    assert "subscription(s) listed in your topic." in out


def test_publisher_example(capsys):
    import publisher_example

    publisher_example.publish_messages(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID,
    )
    out, _ = capsys.readouterr()
    assert "Published a message" in out


def test_publish_with_custom_attributes_example(zonal_topic, capsys):
    import publish_with_custom_attributes_example

    publish_with_custom_attributes_example.publish_with_custom_attributes(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID,
    )
    out, _ = capsys.readouterr()
    assert (
        f"Finished publishing a message with custom attributes to {zonal_topic.name}."
        in out
    )


def test_publish_with_odering_key_example(zonal_topic, capsys):
    import publish_with_ordering_key_example

    publish_with_ordering_key_example.publish_with_odering_key(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, 10,
    )
    out, _ = capsys.readouterr()
    assert (
        f"Finished publishing {NUM_MESSAGES} messages with an ordering key to {zonal_topic.name}."
        in out
    )


def test_publish_with_batch_settings_example(zonal_topic, capsys):
    import publish_with_batch_settings_example

    publish_with_batch_settings_example.publish_with_batch_settings(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, NUM_MESSAGES,
    )
    out, _ = capsys.readouterr()
    assert (
        f"Finished publishing {NUM_MESSAGES} messages with batch settings to {zonal_topic.name}."
        in out
    )


def test_subscriber_example(subscription, capsys):
    import subscriber_example

    subscriber_example.receive_messages(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, SUBSCRIPTION_ID, 45,
    )
    out, _ = capsys.readouterr()
    assert f"Listening for messages on {subscription.name}..." in out
    for message in range(NUM_MESSAGES):
        assert f"Received {message}" in out


def test_seek_lite_subscription_example(subscription, capsys):
    import seek_lite_subscription_example

    seek_lite_subscription_example.seek_lite_subscription(
        PROJECT_NUMBER,
        CLOUD_REGION,
        ZONE_ID,
        SUBSCRIPTION_ID,
        BacklogLocation.BEGINNING,
        False,
    )
    out, _ = capsys.readouterr()
    assert "Seek operation" in out


def test_delete_lite_subscription_example(subscription, capsys):
    import delete_lite_subscription_example

    @backoff.on_exception(backoff.expo, AssertionError, max_time=MAX_TIME)
    def eventually_consistent_test():
        delete_lite_subscription_example.delete_lite_subscription(
            PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, SUBSCRIPTION_ID,
        )
        out, _ = capsys.readouterr()
        assert (
            f"{subscription.name} deleted successfully."
            or f"{subscription.name} not found." in out
        )

    eventually_consistent_test()


def test_delete_lite_topic_example(regional_topic, zonal_topic, capsys):
    import delete_lite_topic_example

    @backoff.on_exception(backoff.expo, AssertionError, max_time=MAX_TIME)
    def eventually_consistent_test():
        delete_lite_topic_example.delete_lite_topic(
            PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, True,
        )
        delete_lite_topic_example.delete_lite_topic(
            PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, False,
        )
        out, _ = capsys.readouterr()
        assert (
            f"{regional_topic.name} (reginal topic) deleted successfully."
            or f"{regional_topic.name} not found" in out
        )
        assert (
            f"{zonal_topic.name} (zonal topic) deleted successfully."
            or f"{zonal_topic.name} not found" in out
        )

    eventually_consistent_test()
