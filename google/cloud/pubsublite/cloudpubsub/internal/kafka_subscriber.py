# Copyright 2026 Google LLC
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

import asyncio
import logging
import queue
import threading
from typing import Mapping, Union, Optional, Any, Set, List

from google.pubsub_v1 import PubsubMessage
from google.protobuf.timestamp_pb2 import Timestamp
from google.cloud.pubsub_v1.subscriber.message import Message

from google.cloud.pubsublite.cloudpubsub.internal.single_subscriber import (
    AsyncSingleSubscriber,
)
from google.cloud.pubsublite.cloudpubsub.internal.wrapped_message import (
    WrappedMessage,
    AckId,
)
from google.cloud.pubsublite.types import Partition, SubscriptionPath
from google.cloud.pubsublite.internal.gmk_auth import gcp_oauth_callback

# Lazy import confluent-kafka
confluent_kafka = None
logger = logging.getLogger(__name__)


def _import_confluent_kafka():
    global confluent_kafka
    if confluent_kafka is None:
        try:
            import confluent_kafka as ck
            confluent_kafka = ck
        except ImportError:
            raise ImportError(
                "confluent-kafka is required for MANAGED_KAFKA backend. "
                "Install it using `pip install google-cloud-pubsublite[kafka]` "
                "or `pip install confluent-kafka`."
            )


def _parse_event_time_header(val: bytes) -> Optional[Timestamp]:
    try:
        s = val.decode("utf-8")
        ts = Timestamp()
        if "." in s:
            parts = s.split(".")
            ts.seconds = int(parts[0])
            # Pad nanos if needed (Go writes %09d, so it should be 9 digits)
            nanos_str = parts[1]
            if len(nanos_str) < 9:
                nanos_str = nanos_str.ljust(9, "0")
            ts.nanos = int(nanos_str[:9])
        else:
            ts.seconds = int(s)
            ts.nanos = 0
        return ts
    except Exception as e:
        logger.warning(f"Failed to parse event time header {val}: {e}")
        return None


class KafkaAsyncSingleSubscriber(AsyncSingleSubscriber):
    """A Kafka-based AsyncSingleSubscriber that consumes from Google Managed Kafka."""

    def __init__(
        self,
        subscription: SubscriptionPath,
        fixed_partitions: Optional[Set[Partition]],
        bootstrap_servers: str,
        kafka_topic: str,
        kafka_properties: Optional[Mapping[str, Any]] = None,
    ):
        _import_confluent_kafka()
        self._subscription = subscription
        self._fixed_partitions = fixed_partitions
        self._bootstrap_servers = bootstrap_servers
        self._kafka_topic = kafka_topic
        self._kafka_properties = kafka_properties

        self._consumer = None
        self._running = False
        self._poll_thread = None
        self._loop = None
        self._queue = asyncio.Queue()
        self._commit_queue = queue.Queue()

    async def __aenter__(self):
        self._loop = asyncio.get_running_loop()
        group_id = str(self._subscription).replace("/", "-")

        config = {
            "bootstrap.servers": self._bootstrap_servers,
            "group.id": group_id,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "OAUTHBEARER",
            "oauth_cb": gcp_oauth_callback,
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
        }
        if self._kafka_properties:
            config.update(self._kafka_properties)

        self._consumer = confluent_kafka.Consumer(config)

        if self._fixed_partitions:
            partitions = [
                confluent_kafka.TopicPartition(self._kafka_topic, p.value)
                for p in self._fixed_partitions
            ]
            self._consumer.assign(partitions)
        else:
            self._consumer.subscribe([self._kafka_topic])

        self._running = True
        self._poll_thread = threading.Thread(
            target=self._poll_loop,
            name=f"kafka-subscriber-poll-{group_id}",
            daemon=True,
        )
        self._poll_thread.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._running = False
        if self._poll_thread and self._poll_thread.is_alive():
            # We must run join in executor to avoid blocking loop
            await self._loop.run_in_executor(None, self._poll_thread.join)
        if self._consumer:
            # Close consumer in executor too as it might block
            await self._loop.run_in_executor(None, self._consumer.close)

    def _poll_loop(self):
        while self._running:
            # 1. Process pending commits
            self._process_commits()

            # 2. Poll for messages
            # Use short timeout to allow quick shutdown and commit processing
            msg = self._consumer.poll(0.1)
            if msg is None:
                continue
            if msg.error():
                # Handle error
                if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Kafka consumer error: {msg.error()}")
                    # We should probably fail the subscriber here.
                    # In asyncio, we can propagate exception to the queue.
                    self._loop.call_soon_threadsafe(
                        self._queue.put_nowait, msg.error()
                    )
                    break

            # 3. Process message
            try:
                wrapped_msg = self._convert_message(msg)
                self._loop.call_soon_threadsafe(self._queue.put_nowait, wrapped_msg)
            except Exception as e:
                logger.exception("Failed to process consumer record")

    def _process_commits(self):
        latest_offsets = {}
        while True:
            try:
                partition, offset = self._commit_queue.get_nowait()
                latest_offsets[partition] = max(
                    latest_offsets.get(partition, -1), offset
                )
            except queue.Empty:
                break

        if latest_offsets:
            offsets_to_commit = [
                confluent_kafka.TopicPartition(self._kafka_topic, p, o + 1)
                for p, o in latest_offsets.items()
            ]
            try:
                # Commit asynchronously
                self._consumer.commit(offsets=offsets_to_commit, asynchronous=True)
            except Exception as e:
                logger.error(f"Failed to commit offsets: {e}")

    def _on_ack(self, ack_id: AckId, should_ack: bool):
        if should_ack:
            self._commit_queue.put((ack_id.generation, ack_id.offset))
        else:
            # Nack behavior: just log, don't commit.
            # Redelivery will happen on rebalance or restart.
            logger.info(
                f"Message nacked, offset {ack_id.offset} on partition {ack_id.generation} will not be committed."
            )

    def _convert_message(self, msg) -> Message:
        pb = PubsubMessage.meta.pb()
        if msg.value() is not None:
            pb.data = msg.value()
        if msg.key() is not None:
            pb.ordering_key = msg.key().decode("utf-8", errors="replace")

        # Convert timestamp
        ts_type, ts_val = msg.timestamp()
        if ts_type != confluent_kafka.TIMESTAMP_NOT_AVAILABLE and ts_val > 0:
            seconds = ts_val // 1000
            nanos = (ts_val % 1000) * 1_000_000
            pb.publish_time.seconds = seconds
            pb.publish_time.nanos = nanos

        # Convert headers
        headers = msg.headers()
        header_counts = {}
        if headers:
            for k, v in headers:
                if k == "pubsublite.event_time":
                    ts = _parse_event_time_header(v)
                    if ts:
                        from google.cloud.pubsublite.cloudpubsub.message_transforms import (
                            _encode_attribute_event_time_proto,
                        )

                        pb.attributes[
                            "x-goog-pubsublite-event-time"
                        ] = _encode_attribute_event_time_proto(ts)
                    continue

                # Handle duplicates by appending index suffix
                count = header_counts.get(k, 0)
                if count == 0:
                    pb.attributes[k] = v.decode("utf-8", errors="replace")
                else:
                    pb.attributes[f"{k}.{count}"] = v.decode(
                        "utf-8", errors="replace"
                    )
                header_counts[k] = count + 1

        # Add Kafka metadata
        pb.attributes["x-kafka-topic"] = msg.topic()
        pb.attributes["x-kafka-partition"] = str(msg.partition())
        pb.attributes["x-kafka-offset"] = str(msg.offset())
        pb.attributes["x-kafka-timestamp-ms"] = str(ts_val)

        # Standard message wrapper needs AckId
        # We map generation -> partition, offset -> offset
        ack_id = AckId(generation=msg.partition(), offset=msg.offset())

        # Wrap it in standard Message class
        # We wrap the proto-plus Message which wraps the pb
        from google.pubsub_v1 import PubsubMessage as ProtoPlusPubsubMessage

        wrapped_pb = ProtoPlusPubsubMessage()
        wrapped_pb._pb = pb

        # Message ID is topic:partition:offset
        wrapped_pb.message_id = f"{msg.topic()}:{msg.partition()}:{msg.offset()}"

        return WrappedMessage(
            pb=wrapped_pb._pb,
            ack_id=ack_id,
            ack_handler=self._on_ack,
        )

    async def read(self) -> List[Message]:
        # Wait for at least one item (could be message or error)
        item = await self._queue.get()
        if isinstance(item, Exception):
            raise item

        batch = [item]
        # Pull more if available
        while not self._queue.empty() and len(batch) < 100:
            next_item = self._queue.get_nowait()
            if isinstance(next_item, Exception):
                raise next_item
            batch.append(next_item)
        return batch
