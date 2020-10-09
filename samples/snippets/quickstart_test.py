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
from google.cloud.pubsublite.location import CloudRegion, CloudZone
from google.cloud.pubsublite.make_admin_client import make_admin_client
from google.cloud.pubsublite.paths import SubscriptionPath, TopicPath
import pytest


project_number = os.environ["GOOGLE_CLOUD_PROJECT_NUMBER"]
cloud_region = "us-central1"
zone_id = ["a", "b", "c"][random.randint(0, 2)]
uuid_hex = uuid.uuid4().hex
topic_id = "py-lite-topic-" + uuid_hex
subscription_id = "py-lite-subscription-" + uuid_hex
num_partitions = 1
num_messages = 10
# Allow 120s for tests to run. The same topic and subscription are
# used for testing in different runtimes, this prevents them from
# geting torn down too early.
max_time = 120


@pytest.fixture(scope="module")
def client():
    yield make_admin_client(cloud_region)


@pytest.fixture(scope="module")
def topic_path(client):
    location = CloudZone(CloudRegion(cloud_region), zone_id)
    topic_path = str(TopicPath(project_number, location, topic_id))
    yield topic_path
    try:
        client.delete_topic(topic_path)
    except NotFound:
        pass


@pytest.fixture(scope="module")
def subscription_path(client):
    location = CloudZone(CloudRegion(cloud_region), zone_id)
    subscription_path = str(SubscriptionPath(project_number, location, subscription_id))
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
        num_partitions,
    )
    out, _ = capsys.readouterr()
    assert "created successfully." in out


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
    assert "updated successfully." in out


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
    assert f"has {num_partitions} partition(s)." in out


def test_list_lite_topics_example(topic_path, capsys):
    import list_lite_topics_example

    topic_path_object = TopicPath.parse(topic_path)
    list_lite_topics_example.list_lite_topics(
        topic_path_object.project_number,
        topic_path_object.location.region.name,
        topic_path_object.location.zone_id,
    )
    out, _ = capsys.readouterr()
    assert "topic(s) listed." in out


def test_create_lite_subscription(subscription_path, topic_path, capsys):
    import create_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)
    topic_path_object = TopicPath.parse(topic_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=max_time)
    def eventually_consistent_test():
        create_lite_subscription_example.create_lite_subscription(
            subscription_path_object.project_number,
            subscription_path_object.location.region.name,
            subscription_path_object.location.zone_id,
            topic_path_object.name,
            subscription_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert "created successfully." in out

    eventually_consistent_test()


def test_update_lite_subscription_example(subscription_path, capsys):
    import update_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=max_time)
    def eventually_consistent_test():
        update_lite_subscription_example.update_lite_subscription(
            subscription_path_object.project_number,
            subscription_path_object.location.region.name,
            subscription_path_object.location.zone_id,
            subscription_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert "updated successfully." in out

    eventually_consistent_test()


def test_get_lite_subscription(subscription_path, capsys):
    import get_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=max_time)
    def eventually_consistent_test():
        get_lite_subscription_example.get_lite_subscription(
            subscription_path_object.project_number,
            subscription_path_object.location.region.name,
            subscription_path_object.location.zone_id,
            subscription_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert "exists." in out

    eventually_consistent_test()


def test_list_lite_subscriptions_in_project(subscription_path, capsys):
    import list_lite_subscriptions_in_project_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=max_time)
    def eventually_consistent_test():
        list_lite_subscriptions_in_project_example.list_lite_subscriptions_in_project(
            subscription_path_object.project_number,
            subscription_path_object.location.region.name,
            subscription_path_object.location.zone_id,
        )
        out, _ = capsys.readouterr()
        assert "subscription(s) listed in your project and location." in out

    eventually_consistent_test()


def test_list_lite_subscriptions_in_topic(topic_path, subscription_path, capsys):
    import list_lite_subscriptions_in_topic_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)
    topic_path_object = TopicPath.parse(topic_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=max_time)
    def eventually_consistent_test():
        list_lite_subscriptions_in_topic_example.list_lite_subscriptions_in_topic(
            subscription_path_object.project_number,
            subscription_path_object.location.region.name,
            subscription_path_object.location.zone_id,
            topic_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert "subscription(s) listed" in out

    eventually_consistent_test()


def test_publisher_example(capsys):
    import publisher_example

    publisher_example.publish_messages(
        project_number, cloud_region, zone_id, topic_id, num_messages
    )
    out, _ = capsys.readouterr()
    assert f"Finished publishing {num_messages} messages." in out


# def test_publish_with_custom_attributes_example(capsys):
#     import publish_with_custom_attributes_example

#     publish_with_custom_attributes_example.publish_with_custom_attributes(
#         project_number, cloud_region, zone_id, topic_id, num_messages
#     )
#     out, _ = capsys.readouterr()
#     assert f"Finished publishing {num_messages} messages with custom attributes." in out


# def test_publish_with_odering_key_example(capsys):
#     import publish_with_ordering_key_example

#     publish_with_ordering_key_example.publish_with_odering_key(
#         project_number, cloud_region, zone_id, topic_id, num_messages
#     )
#     out, _ = capsys.readouterr()
#     assert f"Finished publishing {num_messages} messages with an ordering key." in out


def test_delete_lite_subscription_example(subscription_path, capsys):
    import delete_lite_subscription_example

    subscription_path_object = SubscriptionPath.parse(subscription_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=max_time)
    def eventually_consistent_test():
        delete_lite_subscription_example.delete_lite_subscription(
            subscription_path_object.project_number,
            subscription_path_object.location.region.name,
            subscription_path_object.location.zone_id,
            subscription_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert "deleted successfully." in out

    eventually_consistent_test()


def test_delete_lite_topic_example(topic_path, capsys):
    import delete_lite_topic_example

    topic_path_object = TopicPath.parse(topic_path)

    @backoff.on_exception(backoff.expo, AssertionError, max_time=max_time)
    def eventually_consistent_test():
        delete_lite_topic_example.delete_lite_topic(
            topic_path_object.project_number,
            topic_path_object.location.region.name,
            topic_path_object.location.zone_id,
            topic_path_object.name,
        )
        out, _ = capsys.readouterr()
        assert "deleted successfully." in out

    eventually_consistent_test()
