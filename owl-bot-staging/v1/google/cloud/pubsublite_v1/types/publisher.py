# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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
#
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.pubsublite_v1.types import common


__protobuf__ = proto.module(
    package='google.cloud.pubsublite.v1',
    manifest={
        'InitialPublishRequest',
        'InitialPublishResponse',
        'MessagePublishRequest',
        'MessagePublishResponse',
        'PublishRequest',
        'PublishResponse',
    },
)


class InitialPublishRequest(proto.Message):
    r"""The first request that must be sent on a newly-opened stream.

    Attributes:
        topic (str):
            The topic to which messages will be written.
        partition (int):
            The partition within the topic to which messages will be
            written. Partitions are zero indexed, so ``partition`` must
            be in the range [0, topic.num_partitions).
        client_id (bytes):
            Unique identifier for a publisher client. If
            set, enables publish idempotency within a
            publisher client session.
            The length of this field must be exactly 16
            bytes long and should be populated with a 128
            bit uuid, generated by standard uuid algorithms
            like uuid1 or uuid4. The same identifier should
            be reused following disconnections with
            retryable stream errors.
    """

    topic: str = proto.Field(
        proto.STRING,
        number=1,
    )
    partition: int = proto.Field(
        proto.INT64,
        number=2,
    )
    client_id: bytes = proto.Field(
        proto.BYTES,
        number=3,
    )


class InitialPublishResponse(proto.Message):
    r"""Response to an InitialPublishRequest.
    """


class MessagePublishRequest(proto.Message):
    r"""Request to publish messages to the topic.

    Attributes:
        messages (MutableSequence[google.cloud.pubsublite_v1.types.PubSubMessage]):
            The messages to publish.
        first_sequence_number (int):
            The sequence number corresponding to the first message in
            ``messages``. Messages within a batch are ordered and the
            sequence numbers of all subsequent messages in the batch are
            assumed to be incremental.

            Sequence numbers are assigned at the message level and the
            first message published in a publisher client session must
            have a sequence number of 0. All messages must have
            contiguous sequence numbers, which uniquely identify the
            messages accepted by the publisher client. Since messages
            are ordered, the client only needs to specify the sequence
            number of the first message in a published batch. The server
            deduplicates messages with the same sequence number from the
            same publisher ``client_id``.
    """

    messages: MutableSequence[common.PubSubMessage] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=common.PubSubMessage,
    )
    first_sequence_number: int = proto.Field(
        proto.INT64,
        number=2,
    )


class MessagePublishResponse(proto.Message):
    r"""Response to a MessagePublishRequest.

    Attributes:
        start_cursor (google.cloud.pubsublite_v1.types.Cursor):
            The cursor of the first published message in
            the batch. The cursors for any remaining
            messages in the batch are guaranteed to be
            sequential.
        cursor_ranges (MutableSequence[google.cloud.pubsublite_v1.types.MessagePublishResponse.CursorRange]):
            Cursors for messages published in the batch.
            There will exist multiple ranges when cursors
            are not contiguous within the batch.
            The cursor ranges may not account for all
            messages in the batch when publish idempotency
            is enabled. A missing range indicates that
            cursors could not be determined for messages
            within the range, as they were deduplicated and
            the necessary data was not available at publish
            time. These messages will have offsets when
            received by a subscriber.
    """

    class CursorRange(proto.Message):
        r"""Cursors for a subrange of published messages.

        Attributes:
            start_cursor (google.cloud.pubsublite_v1.types.Cursor):
                The cursor of the message at the start index.
                The cursors for remaining messages up to the end
                index (exclusive) are sequential.
            start_index (int):
                Index of the message in the published batch
                that corresponds to the start cursor. Inclusive.
            end_index (int):
                Index of the last message in this range.
                Exclusive.
        """

        start_cursor: common.Cursor = proto.Field(
            proto.MESSAGE,
            number=1,
            message=common.Cursor,
        )
        start_index: int = proto.Field(
            proto.INT32,
            number=2,
        )
        end_index: int = proto.Field(
            proto.INT32,
            number=3,
        )

    start_cursor: common.Cursor = proto.Field(
        proto.MESSAGE,
        number=1,
        message=common.Cursor,
    )
    cursor_ranges: MutableSequence[CursorRange] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message=CursorRange,
    )


class PublishRequest(proto.Message):
    r"""Request sent from the client to the server on a stream.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        initial_request (google.cloud.pubsublite_v1.types.InitialPublishRequest):
            Initial request on the stream.

            This field is a member of `oneof`_ ``request_type``.
        message_publish_request (google.cloud.pubsublite_v1.types.MessagePublishRequest):
            Request to publish messages.

            This field is a member of `oneof`_ ``request_type``.
    """

    initial_request: 'InitialPublishRequest' = proto.Field(
        proto.MESSAGE,
        number=1,
        oneof='request_type',
        message='InitialPublishRequest',
    )
    message_publish_request: 'MessagePublishRequest' = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof='request_type',
        message='MessagePublishRequest',
    )


class PublishResponse(proto.Message):
    r"""Response to a PublishRequest.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        initial_response (google.cloud.pubsublite_v1.types.InitialPublishResponse):
            Initial response on the stream.

            This field is a member of `oneof`_ ``response_type``.
        message_response (google.cloud.pubsublite_v1.types.MessagePublishResponse):
            Response to publishing messages.

            This field is a member of `oneof`_ ``response_type``.
    """

    initial_response: 'InitialPublishResponse' = proto.Field(
        proto.MESSAGE,
        number=1,
        oneof='response_type',
        message='InitialPublishResponse',
    )
    message_response: 'MessagePublishResponse' = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof='response_type',
        message='MessagePublishResponse',
    )


__all__ = tuple(sorted(__protobuf__.manifest))
