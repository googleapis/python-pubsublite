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

import datetime

import pytest
from google.api_core.exceptions import InvalidArgument
from google.protobuf.timestamp_pb2 import Timestamp
from google.pubsub_v1 import PubsubMessage

from google.cloud.pubsublite.cloudpubsub import MessageTransformer
from google.cloud.pubsublite.cloudpubsub.message_transforms import (
    PUBSUB_LITE_EVENT_TIME,
    to_cps_subscribe_message,
    encode_attribute_event_time,
    from_cps_publish_message,
    add_id_to_cps_subscribe_transformer,
)
from google.cloud.pubsublite.types import Partition, MessageMetadata
from google.cloud.pubsublite_v1 import (
    SequencedMessage,
    Cursor,
    PubSubMessage,
    AttributeValues,
)

NOT_UTF8 = bytes.fromhex("ffff")


def test_invalid_subscribe_transform_key():
    with pytest.raises(InvalidArgument):
        to_cps_subscribe_message(
            SequencedMessage(
                message=PubSubMessage(key=NOT_UTF8),
                publish_time=Timestamp(),
                cursor=Cursor(offset=10),
                size_bytes=10,
            )
        )


def test_invalid_subscribe_contains_magic_attribute():
    with pytest.raises(InvalidArgument):
        to_cps_subscribe_message(
            SequencedMessage(
                message=PubSubMessage(
                    key=b"def",
                    attributes={
                        PUBSUB_LITE_EVENT_TIME: AttributeValues(values=[b"abc"])
                    },
                ),
                publish_time=Timestamp(seconds=10),
                cursor=Cursor(offset=10),
                size_bytes=10,
            )
        )


def test_invalid_subscribe_contains_multiple_attributes():
    with pytest.raises(InvalidArgument):
        to_cps_subscribe_message(
            SequencedMessage(
                message=PubSubMessage(
                    key=b"def",
                    attributes={"xyz": AttributeValues(values=[b"abc", b""])},
                ),
                publish_time=Timestamp(seconds=10),
                cursor=Cursor(offset=10),
                size_bytes=10,
            )
        )


def test_invalid_subscribe_contains_non_utf8_attributes():
    with pytest.raises(InvalidArgument):
        to_cps_subscribe_message(
            SequencedMessage(
                message=PubSubMessage(
                    key=b"def", attributes={"xyz": AttributeValues(values=[NOT_UTF8])}
                ),
                publish_time=Timestamp(seconds=10),
                cursor=Cursor(offset=10),
                size_bytes=10,
            )
        )


def test_subscribe_transform_correct():
    expected = PubsubMessage(
        data=b"xyz",
        ordering_key="def",
        attributes={
            "x": "abc",
            "y": "abc",
            PUBSUB_LITE_EVENT_TIME: encode_attribute_event_time(
                Timestamp(seconds=55).ToDatetime()
            ),
        },
        publish_time=Timestamp(seconds=10),
    )
    result = to_cps_subscribe_message(
        SequencedMessage(
            message=PubSubMessage(
                data=b"xyz",
                key=b"def",
                event_time=Timestamp(seconds=55),
                attributes={
                    "x": AttributeValues(values=[b"abc"]),
                    "y": AttributeValues(values=[b"abc"]),
                },
            ),
            publish_time=Timestamp(seconds=10),
            cursor=Cursor(offset=10),
            size_bytes=10,
        )
    )
    assert result == expected


def test_wrapped_sets_id_error():
    wrapped = add_id_to_cps_subscribe_transformer(
        Partition(1),
        MessageTransformer.of_callable(lambda x: PubsubMessage(message_id="a")),
    )
    with pytest.raises(InvalidArgument):
        wrapped.transform(
            SequencedMessage(
                message=PubSubMessage(
                    data=b"xyz",
                    key=b"def",
                    event_time=Timestamp(seconds=55),
                    attributes={
                        "x": AttributeValues(values=[b"abc"]),
                        "y": AttributeValues(values=[b"abc"]),
                    },
                ),
                publish_time=Timestamp(seconds=10),
                cursor=Cursor(offset=10),
                size_bytes=10,
            )
        )


def test_wrapped_successful():
    wrapped = add_id_to_cps_subscribe_transformer(
        Partition(1), MessageTransformer.of_callable(to_cps_subscribe_message)
    )
    expected = PubsubMessage(
        data=b"xyz",
        ordering_key="def",
        attributes={
            "x": "abc",
            "y": "abc",
            PUBSUB_LITE_EVENT_TIME: encode_attribute_event_time(
                Timestamp(seconds=55).ToDatetime()
            ),
        },
        message_id=MessageMetadata(Partition(1), Cursor(offset=10)).encode(),
        publish_time=Timestamp(seconds=10),
    )
    result = wrapped.transform(
        SequencedMessage(
            message=PubSubMessage(
                data=b"xyz",
                key=b"def",
                event_time=Timestamp(seconds=55),
                attributes={
                    "x": AttributeValues(values=[b"abc"]),
                    "y": AttributeValues(values=[b"abc"]),
                },
            ),
            publish_time=Timestamp(seconds=10),
            cursor=Cursor(offset=10),
            size_bytes=10,
        )
    )
    assert result == expected


def test_publish_invalid_event_time():
    with pytest.raises(InvalidArgument):
        from_cps_publish_message(
            PubsubMessage(
                attributes={PUBSUB_LITE_EVENT_TIME: "probably not an encoded proto"}
            )
        )


def test_publish_valid_transform():
    now = datetime.datetime.now()
    expected = PubSubMessage(
        data=b"xyz",
        key=b"def",
        event_time=now,
        attributes={
            "x": AttributeValues(values=[b"abc"]),
            "y": AttributeValues(values=[b"abc"]),
        },
    )
    result = from_cps_publish_message(
        PubsubMessage(
            data=b"xyz",
            ordering_key="def",
            attributes={
                "x": "abc",
                "y": "abc",
                PUBSUB_LITE_EVENT_TIME: encode_attribute_event_time(now),
            },
        )
    )
    assert result == expected
