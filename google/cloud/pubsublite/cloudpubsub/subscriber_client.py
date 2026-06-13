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

from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional, Union, Set, AsyncIterator, Any, Mapping

from google.cloud.pubsublite.cloudpubsub.messaging_backend import MessagingBackend
from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials
from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
from google.cloud.pubsub_v1.subscriber.message import Message

from google.cloud.pubsublite.cloudpubsub.reassignment_handler import ReassignmentHandler
from google.cloud.pubsublite.cloudpubsub.internal.make_subscriber import (
    make_async_subscriber,
)
from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_async_subscriber_client import (
    MultiplexedAsyncSubscriberClient,
)
from google.cloud.pubsublite.cloudpubsub.internal.multiplexed_subscriber_client import (
    MultiplexedSubscriberClient,
)
from google.cloud.pubsublite.cloudpubsub.message_transformer import MessageTransformer
from google.cloud.pubsublite.cloudpubsub.nack_handler import NackHandler
from google.cloud.pubsublite.cloudpubsub.subscriber_client_interface import (
    SubscriberClientInterface,
    AsyncSubscriberClientInterface,
    MessageCallback,
)
from google.cloud.pubsublite.internal.constructable_from_service_account import (
    ConstructableFromServiceAccount,
)
from google.cloud.pubsublite.internal.require_started import RequireStarted
from google.cloud.pubsublite.types import (
    FlowControlSettings,
    Partition,
    SubscriptionPath,
)
from overrides import overrides


class SubscriberClient(SubscriberClientInterface, ConstructableFromServiceAccount):
    """
    A SubscriberClient reads messages similar to Google Pub/Sub.
    Any subscribe failures are unlikely to succeed if retried.

    Must be used in a `with` block or have __enter__() called before use.
    """

    _impl: SubscriberClientInterface
    _require_started: RequireStarted

    def __init__(
        self,
        *,
        executor: Optional[ThreadPoolExecutor] = None,
        nack_handler: Optional[NackHandler] = None,
        reassignment_handler: Optional[ReassignmentHandler] = None,
        message_transformer: Optional[MessageTransformer] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
        backend: MessagingBackend = MessagingBackend.PUBSUB_LITE,
        bootstrap_servers: Optional[str] = None,
        kafka_topic: Optional[str] = None,
        kafka_properties: Optional[Mapping[str, Any]] = None,
    ):
        """
        Create a new SubscriberClient.

        Args:
            executor: A ThreadPoolExecutor to use. The client will shut it down on __exit__.
            nack_handler: A handler for when `nack()` is called.
            reassignment_handler: A handler for when partitions are reassigned. Only used for PUBSUB_LITE backend.
            message_transformer: A transformer from Pub/Sub Lite messages to Cloud Pub/Sub messages.
            credentials: If provided, the credentials to use when connecting. Only used for PUBSUB_LITE backend.
            transport: The transport to use. Only used for PUBSUB_LITE backend.
            client_options: The client options to use when connecting. Only used for PUBSUB_LITE backend.
            backend: The messaging backend to use.
            bootstrap_servers: The Kafka bootstrap servers. Required if backend is MANAGED_KAFKA.
            kafka_topic: The Kafka topic name. Required if backend is MANAGED_KAFKA.
            kafka_properties: Additional configuration properties for the Kafka consumer. Only used if backend is MANAGED_KAFKA.
        """
        if backend == MessagingBackend.MANAGED_KAFKA:
            if not bootstrap_servers:
                raise ValueError(
                    "bootstrap_servers must be set when backend is MANAGED_KAFKA"
                )
            if not kafka_topic:
                raise ValueError(
                    "kafka_topic must be set when backend is MANAGED_KAFKA"
                )

        if executor is None:
            executor = ThreadPoolExecutor()
        self._impl = MultiplexedSubscriberClient(
            executor,
            lambda subscription, partitions, settings: make_async_subscriber(
                subscription=subscription,
                transport=transport,
                per_partition_flow_control_settings=settings,
                nack_handler=nack_handler,
                reassignment_handler=reassignment_handler,
                message_transformer=message_transformer,
                fixed_partitions=partitions,
                credentials=credentials,
                client_options=client_options,
                backend=backend,
                bootstrap_servers=bootstrap_servers,
                kafka_topic=kafka_topic,
                kafka_properties=kafka_properties,
            ),
        )
        self._require_started = RequireStarted()

    @overrides
    def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        callback: MessageCallback,
        per_partition_flow_control_settings: FlowControlSettings,
        fixed_partitions: Optional[Set[Partition]] = None,
    ) -> StreamingPullFuture:
        self._require_started.require_started()
        return self._impl.subscribe(
            subscription,
            callback,
            per_partition_flow_control_settings,
            fixed_partitions,
        )

    @overrides
    def __enter__(self):
        self._require_started.__enter__()
        self._impl.__enter__()
        return self

    @overrides
    def __exit__(self, exc_type, exc_value, traceback):
        self._impl.__exit__(exc_type, exc_value, traceback)
        self._require_started.__exit__(exc_type, exc_value, traceback)


class AsyncSubscriberClient(
    AsyncSubscriberClientInterface, ConstructableFromServiceAccount
):
    """
    An AsyncSubscriberClient reads messages similar to Google Pub/Sub, but must be used in an
    async context.
    Any subscribe failures are unlikely to succeed if retried.

    Must be used in an `async with` block or have __aenter__() awaited before use.
    """

    _impl: AsyncSubscriberClientInterface
    _require_started: RequireStarted

    def __init__(
        self,
        *,
        nack_handler: Optional[NackHandler] = None,
        reassignment_handler: Optional[ReassignmentHandler] = None,
        message_transformer: Optional[MessageTransformer] = None,
        credentials: Optional[Credentials] = None,
        transport: str = "grpc_asyncio",
        client_options: Optional[ClientOptions] = None,
        backend: MessagingBackend = MessagingBackend.PUBSUB_LITE,
        bootstrap_servers: Optional[str] = None,
        kafka_topic: Optional[str] = None,
        kafka_properties: Optional[Mapping[str, Any]] = None,
    ):
        """
        Create a new AsyncSubscriberClient.

        Args:
            nack_handler: A handler for when `nack()` is called.
            reassignment_handler: A handler for when partitions are reassigned. Only used for PUBSUB_LITE backend.
            message_transformer: A transformer from Pub/Sub Lite messages to Cloud Pub/Sub messages.
            credentials: If provided, the credentials to use when connecting. Only used for PUBSUB_LITE backend.
            transport: The transport to use. Only used for PUBSUB_LITE backend.
            client_options: The client options to use when connecting. Only used for PUBSUB_LITE backend.
            backend: The messaging backend to use.
            bootstrap_servers: The Kafka bootstrap servers. Required if backend is MANAGED_KAFKA.
            kafka_topic: The Kafka topic name. Required if backend is MANAGED_KAFKA.
            kafka_properties: Additional configuration properties for the Kafka consumer. Only used if backend is MANAGED_KAFKA.
        """
        if backend == MessagingBackend.MANAGED_KAFKA:
            if not bootstrap_servers:
                raise ValueError(
                    "bootstrap_servers must be set when backend is MANAGED_KAFKA"
                )
            if not kafka_topic:
                raise ValueError(
                    "kafka_topic must be set when backend is MANAGED_KAFKA"
                )

        self._impl = MultiplexedAsyncSubscriberClient(
            lambda subscription, partitions, settings: make_async_subscriber(
                subscription=subscription,
                transport=transport,
                per_partition_flow_control_settings=settings,
                nack_handler=nack_handler,
                reassignment_handler=reassignment_handler,
                message_transformer=message_transformer,
                fixed_partitions=partitions,
                credentials=credentials,
                client_options=client_options,
                backend=backend,
                bootstrap_servers=bootstrap_servers,
                kafka_topic=kafka_topic,
                kafka_properties=kafka_properties,
            )
        )
        self._require_started = RequireStarted()

    @overrides
    async def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        per_partition_flow_control_settings: FlowControlSettings,
        fixed_partitions: Optional[Set[Partition]] = None,
    ) -> AsyncIterator[Message]:
        self._require_started.require_started()
        return await self._impl.subscribe(
            subscription, per_partition_flow_control_settings, fixed_partitions
        )

    @overrides
    async def __aenter__(self):
        self._require_started.__enter__()
        await self._impl.__aenter__()
        return self

    @overrides
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._impl.__aexit__(exc_type, exc_value, traceback)
        self._require_started.__exit__(exc_type, exc_value, traceback)
