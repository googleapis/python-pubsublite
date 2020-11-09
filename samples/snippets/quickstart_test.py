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
from google.api_core.exceptions import NotFound
from google.cloud.pubsublite import AdminClient
from google.cloud.pubsublite.types import (
    CloudRegion,
    CloudZone,
    SubscriptionPath,
    TopicPath,
)
import pytest

PROJECT_NUMBER = os.environ["GOOGLE_CLOUD_PROJECT_NUMBER"]
CLOUD_REGION = "us-central1"
ZONE_ID = ["a", "b", "c"][random.randint(0, 2)]
UUID = uuid.uuid4().hex
TOPIC_ID = "py-lite-topic-" + UUID
SUBSCRIPTION_ID = "py-lite-subscription-" + UUID
NUM_PARTITIONS = 1
NUM_MESSAGES = 10
# Allow 90s for tests to finish.
MAX_TIME = 90


@pytest.fixture(scope="module")
def client():
    yield AdminClient(CLOUD_REGION)


@pytest.fixture(scope="module")
def topic_path(client):
    location = CloudZone(CloudRegion(CLOUD_REGION), ZONE_ID)
    topic_path = str(TopicPath(PROJECT_NUMBER, location, TOPIC_ID))
    yield topic_path
    try:
        client.delete_topic(topic_path)
    except NotFound:
        pass


@pytest.fixture(scope="module")
def subscription_path(client):
    location = CloudZone(CloudRegion(CLOUD_REGION), ZONE_ID)
    subscription_path = str(SubscriptionPath(PROJECT_NUMBER, location, SUBSCRIPTION_ID))
    yield subscription_path
    try:
        client.delete_subscription(subscription_path)
    except NotFound:
        pass


def test_create_lite_topic_example(topic_path, capsys):
    import create_lite_topic_example

    topic_path_object = TopicPath.parse(topic_path)
    create_lite_topic_example.create_lite_topic(
        topic_path_object.project_number,
        topic_path_object.location.region.name,
        topic_path_object.location.zone_id,
        topic_path_object.name,
        NUM_PARTITIONS,
    )
    out, _ = capsys.readouterr()
    assert f"{topic_path} created successfully." in out


def test_update_lite_topic_example(topic_path, capsys):
    import update_lite_topic_example

    topic_path_object = TopicPath.parse(topic_path)
    update_lite_topic_example.update_lite_topic(
        topic_path_object.project_number,
        topic_path_object.location.region.name,
        topic_path_object.location.zone_id,
        topic_path_object.name,
    )
    out, _ = capsys.readouterr()
    assert f"{topic_path} updated successfully." in out


def test_get_lite_topic_example(topic_path, capsys):
    import get_lite_topic_example

    topic_path_object = TopicPath.parse(topic_path)
    get_lite_topic_example.get_lite_topic(
        topic_path_object.project_number,
        topic_path_object.location.region.name,
        topic_path_object.location.zone_id,
        topic_path_object.name,
    )
    out, _ = capsys.readouterr()
    assert f"{topic_path} has {NUM_PARTITIONS} partition(s)." in out


def test_list_lite_topics_example(topic_path, capsys):
    import list_lite_topics_example

    topic_path_object = TopicPath.parse(topic_path)
    list_lite_topics_example.list_lite_topics(
        topic_path_object.project_number,
        topic_path_object.location.region.name,
        topic_path_object.location.zone_id,
    )
    out, _ = capsys.readouterr()
    assert "topic(s) listed in your project and location." in out


def test_create_lite_subscription(subscription_path, topic_path, capsys):
    import create_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)
    topic_path_object = TopicPath.parse(topic_path)

    create_lite_subscription_example.create_lite_subscription(
        subscription_path_object.project_number,
        subscription_path_object.location.region.name,
        subscription_path_object.location.zone_id,
        topic_path_object.name,
        subscription_path_object.name,
    )
    out, _ = capsys.readouterr()
    assert f"{subscription_path} created successfully." in out


def test_update_lite_subscription_example(subscription_path, capsys):
    import update_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    update_lite_subscription_example.update_lite_subscription(
        subscription_path_object.project_number,
        subscription_path_object.location.region.name,
        subscription_path_object.location.zone_id,
        subscription_path_object.name,
    )
    out, _ = capsys.readouterr()
    assert f"{subscription_path} updated successfully." in out


def test_get_lite_subscription(subscription_path, capsys):
    import get_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    get_lite_subscription_example.get_lite_subscription(
        subscription_path_object.project_number,
        subscription_path_object.location.region.name,
        subscription_path_object.location.zone_id,
        subscription_path_object.name,
    )
    out, _ = capsys.readouterr()
    assert f"{subscription_path} exists." in out


def test_list_lite_subscriptions_in_project(subscription_path, capsys):
    import list_lite_subscriptions_in_project_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    list_lite_subscriptions_in_project_example.list_lite_subscriptions_in_project(
        subscription_path_object.project_number,
        subscription_path_object.location.region.name,
        subscription_path_object.location.zone_id,
    )
    out, _ = capsys.readouterr()
    assert "subscription(s) listed in your project and location." in out


def test_list_lite_subscriptions_in_topic(topic_path, subscription_path, capsys):
    import list_lite_subscriptions_in_topic_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)
    topic_path_object = TopicPath.parse(topic_path)

    list_lite_subscriptions_in_topic_example.list_lite_subscriptions_in_topic(
        subscription_path_object.project_number,
        subscription_path_object.location.region.name,
        subscription_path_object.location.zone_id,
        topic_path_object.name,
    )
    out, _ = capsys.readouterr()
    assert "subscription(s) listed in your topic." in out


def test_publisher_example(topic_path, capsys):
    import publisher_example

    publisher_example.publish_messages(PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID)
    out, _ = capsys.readouterr()
    assert "Published a message" in out


def test_publish_with_custom_attributes_example(topic_path, capsys):
    import publish_with_custom_attributes_example

    publish_with_custom_attributes_example.publish_with_custom_attributes(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID
    )
    out, _ = capsys.readouterr()
    assert (
        f"Finished publishing a message with custom attributes to {topic_path}." in out
    )


def test_publish_with_odering_key_example(topic_path, capsys):
    import publish_with_ordering_key_example

    publish_with_ordering_key_example.publish_with_odering_key(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, NUM_MESSAGES
    )
    out, _ = capsys.readouterr()
    assert (
        f"Finished publishing {NUM_MESSAGES} messages with an ordering key to {topic_path}."
        in out
    )


def test_publish_with_batch_settings_example(topic_path, capsys):
    import publish_with_batch_settings_example

    publish_with_batch_settings_example.publish_with_batch_settings(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, TOPIC_ID, NUM_MESSAGES
    )
    out, _ = capsys.readouterr()
    assert (
        f"Finished publishing {NUM_MESSAGES} messages with batch settings to {topic_path}."
        in out
    )


def test_subscriber_example(topic_path, subscription_path, capsys):
    import subscriber_example

    subscriber_example.receive_messages(
        PROJECT_NUMBER, CLOUD_REGION, ZONE_ID, SUBSCRIPTION_ID, 45
    )
    out, _ = capsys.readouterr()
    assert f"Listening for messages on {subscription_path}..." in out
    for message in range(NUM_MESSAGES):
        assert f"Received {message}" in out


def test_delete_lite_subscription_example(subscription_path, capsys):
    import delete_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=MAX_TIME)
    def eventually_consistent_test():
        delete_lite_subscription_example.delete_lite_subscription(
            subscription_path_object.project_number,
            subscription_path_object.location.region.name,
            subscription_path_object.location.zone_id,
            subscription_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert f"{subscription_path} deleted successfully." in out

    eventually_consistent_test()


def test_delete_lite_topic_example(topic_path, capsys):
    import delete_lite_topic_example

    topic_path_object = TopicPath.parse(topic_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=MAX_TIME)
    def eventually_consistent_test():
        delete_lite_topic_example.delete_lite_topic(
            topic_path_object.project_number,
            topic_path_object.location.region.name,
            topic_path_object.location.zone_id,
            topic_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert f"{topic_path} deleted successfully." in out

    eventually_consistent_test()
