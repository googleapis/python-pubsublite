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

import create_lite_topic_example

uuid_hex = uuid.uuid4().hex
project_number = os.environ["GOOGLE_CLOUD_PROJECT_NUMBER"]
topic_id = "py-lite-topic-" + uuid_hex
cloud_region = "us-central1"
zone_id = ["a", "b", "c"][random.randint(0, 2)]
num_partitions = 1


def test_create_lite_topic(capsys):
    create_lite_topic_example.create_lite_topic(
        project_number, cloud_region, zone_id, topic_id, num_partitions
    )
    out, _ = capsys.readouterr()
    assert "created successfully." in out
