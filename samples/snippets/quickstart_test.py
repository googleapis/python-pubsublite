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

from google.cloud.pubsublite.make_admin_client import make_admin_client
from google.cloud.pubsublite.paths import LocationPath, TopicPath
from google.cloud.pubsublite.location import CloudRegion, CloudZone
import pytest

import create_lite_topic_example, update_lite_topic_example, get_lite_topic_example, list_lite_topics_example, delete_lite_topic_example

uuid_hex = uuid.uuid4().hex
project_number = os.environ["GOOGLE_CLOUD_PROJECT_NUMBER"]
topic_id = "py-lite-topic-" + uuid_hex
cloud_region = "us-central1"
zone_id = ["a", "b", "c"][random.randint(0, 2)]
num_partitions = 1


@pytest.fixture(scope="module")
def client():
    yield make_admin_client(cloud_region)


@pytest.topic(scope="module")
def topic_path(client):
    location = CloudZone(CloudRegion(cloud_region), zone_id)
    location_path = LocationPath(project_number, location)
    topic_path = str(TopicPath(project_number, location, topic_id))
    yield topic_path
    client.delete_topic(location_path)


def test_create_lite_topic_example(client, capsys):
    create_lite_topic_example.create_lite_topic(
        project_number, cloud_region, zone_id, topic_id, num_partitions
    )
    out, _ = capsys.readouterr()
    assert "created successfully." in out


def test_update_lite_topic_example(client, capsys):
    update_lite_topic_example.update_lite_topic(
        project_number, cloud_region, zone_id, topic_id
    )
    out, _ = capsys.readouterr()
    assert "updated successfully." in out


def test_get_lite_topic_example(client, capsys):
    get_lite_topic_example.get_lite_topic(
        project_number, cloud_region, zone_id, topic_id
    )
    out, _ = capsys.readouterr()
    assert f"has {num_partitions} partition(s)." in out


def test_list_lite_topics_example(client, capsys):
    list_lite_topics_example.list_lite_topics(project_number, cloud_region, zone_id)
    out, _ = capsys.readouterr()
    assert "topic(s) listed." in out


def test_delete_lite_topic_example(client, capsys):
    delete_lite_topic_example.delete_lite_topic(
        project_number, cloud_region, zone_id, topic_id
    )
    out, _ = capsys.readouterr()
    assert "deleted successfully." in out
