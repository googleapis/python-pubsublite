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
from concurrent.futures import Future
import threading
from typing import Mapping, Union, Optional, Any

from google.api_core.exceptions import InternalServerError
from google.cloud.pubsublite.cloudpubsub.publisher_client_interface import (
    PublisherClientInterface,
    AsyncPublisherClientInterface,
)
from google.cloud.pubsublite.types import TopicPath
from google.cloud.pubsublite.internal.gmk_auth import gcp_oauth_callback

# Lazy import confluent-kafka to avoid hard dependency
confluent_kafka = None


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


class KafkaPublisherClient(PublisherClientInterface):
    """A Kafka-based PublisherClient that publishes to Google Managed Kafka."""

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_properties: Optional[Mapping[str, Any]] = None,
    ):
        _import_confluent_kafka()
        config = {
            "bootstrap.servers": bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "OAUTHBEARER",
            "oauth_cb": gcp_oauth_callback,
            "enable.idempotence": True,
        }
        if kafka_properties:
            # Filter out keys we manage, but allow overriding if user insists
            config.update(kafka_properties)

        self._producer = confluent_kafka.Producer(config)
        self._running = True
        self._poll_thread = threading.Thread(
            target=self._poll_loop, name=f"kafka-publisher-poll-{id(self)}", daemon=True
        )
        self._poll_thread.start()

    def _poll_loop(self):
        while self._running:
            self._producer.poll(0.1)

    def publish(
        self,
        topic: Union[TopicPath, str],
        data: bytes,
        ordering_key: str = "",
        **attrs: Mapping[str, str],
    ) -> "Future[str]":
        future = Future()
        headers = []
        for k, v in attrs.items():
            if k == "x-goog-pubsublite-event-time":
                try:
                    from google.cloud.pubsublite.cloudpubsub.message_transforms import (
                        _decode_attribute_event_time_proto,
                    )

                    ts = _decode_attribute_event_time_proto(v)
                    event_time_val = f"{ts.seconds}.{ts.nanos:09d}".encode("utf-8")
                    headers.append(("pubsublite.event_time", event_time_val))
                except Exception:
                    headers.append((k, v.encode("utf-8")))
            else:
                headers.append((k, v.encode("utf-8")))

        key = ordering_key.encode("utf-8") if ordering_key else None
        topic_str = str(topic) if isinstance(topic, TopicPath) else topic

        def delivery_callback(err, msg):
            if err is not None:
                future.set_exception(
                    InternalServerError(f"Kafka publish failed: {err}")
                )
            else:
                # Format message ID as partition:offset to match PSL-like ID
                msg_id = f"{msg.partition()}:{msg.offset()}"
                future.set_result(msg_id)

        try:
            self._producer.produce(
                topic=topic_str,
                value=data,
                key=key,
                headers=headers,
                callback=delivery_callback,
            )
        except Exception as e:
            future.set_exception(e)

        return future

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._shutdown()

    def _shutdown(self):
        self._running = False
        if self._poll_thread.is_alive():
            self._poll_thread.join()
        self._producer.flush()


class AsyncKafkaPublisherClient(AsyncPublisherClientInterface):
    """An asynchronous Kafka-based PublisherClient that publishes to Google Managed Kafka."""

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_properties: Optional[Mapping[str, Any]] = None,
    ):
        _import_confluent_kafka()
        config = {
            "bootstrap.servers": bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "OAUTHBEARER",
            "oauth_cb": gcp_oauth_callback,
            "enable.idempotence": True,
        }
        if kafka_properties:
            config.update(kafka_properties)

        self._producer = confluent_kafka.Producer(config)
        self._running = True
        self._poll_thread = threading.Thread(
            target=self._poll_loop,
            name=f"async-kafka-publisher-poll-{id(self)}",
            daemon=True,
        )
        self._poll_thread.start()

    def _poll_loop(self):
        while self._running:
            self._producer.poll(0.1)

    async def publish(
        self,
        topic: Union[TopicPath, str],
        data: bytes,
        ordering_key: str = "",
        **attrs: Mapping[str, str],
    ) -> str:
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        headers = []
        for k, v in attrs.items():
            if k == "x-goog-pubsublite-event-time":
                try:
                    from google.cloud.pubsublite.cloudpubsub.message_transforms import (
                        _decode_attribute_event_time_proto,
                    )

                    ts = _decode_attribute_event_time_proto(v)
                    event_time_val = f"{ts.seconds}.{ts.nanos:09d}".encode("utf-8")
                    headers.append(("pubsublite.event_time", event_time_val))
                except Exception:
                    headers.append((k, v.encode("utf-8")))
            else:
                headers.append((k, v.encode("utf-8")))

        key = ordering_key.encode("utf-8") if ordering_key else None
        topic_str = str(topic) if isinstance(topic, TopicPath) else topic

        def delivery_callback(err, msg):
            if err is not None:
                loop.call_soon_threadsafe(
                    future.set_exception,
                    InternalServerError(f"Kafka publish failed: {err}"),
                )
            else:
                msg_id = f"{msg.partition()}:{msg.offset()}"
                loop.call_soon_threadsafe(future.set_result, msg_id)

        try:
            self._producer.produce(
                topic=topic_str,
                value=data,
                key=key,
                headers=headers,
                callback=delivery_callback,
            )
        except Exception as e:
            future.set_exception(e)

        return await future

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._shutdown)

    def _shutdown(self):
        self._running = False
        if self._poll_thread.is_alive():
            self._poll_thread.join()
        self._producer.flush()
