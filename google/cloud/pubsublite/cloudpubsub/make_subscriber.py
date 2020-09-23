from typing import Optional, Mapping, Set, AsyncIterator
from uuid import uuid4

from google.api_core.client_options import ClientOptions
from google.auth.credentials import Credentials

from google.cloud.pubsublite.cloudpubsub.flow_control_settings import FlowControlSettings
from google.cloud.pubsublite.cloudpubsub.internal.ack_set_tracker_impl import AckSetTrackerImpl
from google.cloud.pubsublite.cloudpubsub.internal.assigning_subscriber import PartitionSubscriberFactory, \
  AssigningSubscriber
from google.cloud.pubsublite.cloudpubsub.internal.single_partition_subscriber import SinglePartitionSubscriber
from google.cloud.pubsublite.cloudpubsub.message_transformer import MessageTransformer, DefaultMessageTransformer
from google.cloud.pubsublite.cloudpubsub.nack_handler import NackHandler, DefaultNackHandler
from google.cloud.pubsublite.cloudpubsub.subscriber import AsyncSubscriber
from google.cloud.pubsublite.endpoints import regional_endpoint
from google.cloud.pubsublite.internal.wire.assigner import Assigner
from google.cloud.pubsublite.internal.wire.assigner_impl import AssignerImpl
from google.cloud.pubsublite.internal.wire.committer_impl import CommitterImpl
from google.cloud.pubsublite.internal.wire.fixed_set_assigner import FixedSetAssigner
from google.cloud.pubsublite.internal.wire.gapic_connection import GapicConnectionFactory
from google.cloud.pubsublite.internal.wire.merge_metadata import merge_metadata
from google.cloud.pubsublite.internal.wire.pubsub_context import pubsub_context
from google.cloud.pubsublite.internal.wire.subscriber_impl import SubscriberImpl
from google.cloud.pubsublite.partition import Partition
from google.cloud.pubsublite.paths import SubscriptionPath
from google.cloud.pubsublite.routing_metadata import subscription_routing_metadata
from google.cloud.pubsublite_v1 import SubscribeRequest, InitialSubscribeRequest, StreamingCommitCursorRequest, \
  PartitionAssignmentRequest, InitialPartitionAssignmentRequest, InitialCommitCursorRequest
from google.cloud.pubsublite_v1.services.subscriber_service.async_client import SubscriberServiceAsyncClient
from google.cloud.pubsublite_v1.services.partition_assignment_service.async_client import \
  PartitionAssignmentServiceAsyncClient
from google.cloud.pubsublite_v1.services.cursor_service.async_client import CursorServiceAsyncClient

_DEFAULT_FLUSH_SECONDS = .1


def _make_dynamic_assigner(
    subscription: SubscriptionPath,
    assignment_client: PartitionAssignmentServiceAsyncClient,
    base_metadata: Optional[Mapping[str, str]]) -> Assigner:
  def assignment_connection_factory(requests: AsyncIterator[PartitionAssignmentRequest]):
    return assignment_client.assign_partitions(requests, metadata=list(base_metadata.items()))

  return AssignerImpl(InitialPartitionAssignmentRequest(subscription=str(subscription), client_id=uuid4().bytes),
                      GapicConnectionFactory(assignment_connection_factory))


def _make_partition_subscriber_factory(
    subscription: SubscriptionPath,
    subscribe_client: SubscriberServiceAsyncClient,
    cursor_client: CursorServiceAsyncClient,
    base_metadata: Optional[Mapping[str, str]],
    flow_control_settings: FlowControlSettings,
    nack_handler: NackHandler,
    message_transformer: MessageTransformer
) -> PartitionSubscriberFactory:
  def factory(partition: Partition) -> AsyncSubscriber:
    final_metadata = merge_metadata(base_metadata, subscription_routing_metadata(subscription, partition))

    def subscribe_connection_factory(requests: AsyncIterator[SubscribeRequest]):
      return subscribe_client.subscribe(requests, metadata=list(final_metadata.items()))

    def cursor_connection_factory(requests: AsyncIterator[StreamingCommitCursorRequest]):
      return cursor_client.streaming_commit_cursor(requests, metadata=list(final_metadata.items()))

    wire_subscriber = SubscriberImpl(
      InitialSubscribeRequest(subscription=str(subscription), partition=partition.value),
      _DEFAULT_FLUSH_SECONDS, GapicConnectionFactory(subscribe_connection_factory))
    committer = CommitterImpl(
      InitialCommitCursorRequest(subscription=str(subscription), partition=partition.value),
      _DEFAULT_FLUSH_SECONDS, GapicConnectionFactory(cursor_connection_factory))
    ack_set_tracker = AckSetTrackerImpl(committer)
    return SinglePartitionSubscriber(wire_subscriber, flow_control_settings, ack_set_tracker, nack_handler,
                                     message_transformer)

  return factory


def make_async_subscriber(
    subscription: SubscriptionPath,
    per_partition_flow_control_settings: FlowControlSettings,
    nack_handler: Optional[NackHandler] = None,
    message_transformer: Optional[MessageTransformer] = None,
    fixed_partitions: Optional[Set[Partition]] = None,
    credentials: Optional[Credentials] = None,
    client_options: Optional[ClientOptions] = None,
    metadata: Optional[Mapping[str, str]] = None) -> AsyncSubscriber:
  """
  Make a Pub/Sub Lite AsyncSubscriber.

  Args:
    subscription: The subscription to subscribe to.
    per_partition_flow_control_settings: The flow control settings for each partition subscribed to. Note that these
      settings apply to each partition individually, not in aggregate.
    nack_handler: An optional handler for when nack() is called on a Message. The default will fail the client.
    message_transformer: An optional transformer from Pub/Sub Lite messages to Cloud Pub/Sub messages.
    fixed_partitions: A fixed set of partitions to subscribe to. If not present, will instead use auto-assignment.
    credentials: The credentials to use to connect. GOOGLE_DEFAULT_CREDENTIALS is used if None.
    client_options: Other options to pass to the client. Note that if you pass any you must set api_endpoint.
    metadata: Additional metadata to send with the RPC.

  Returns:
    A new AsyncSubscriber.
  """
  metadata = merge_metadata(pubsub_context(framework="CLOUD_PUBSUB_SHIM"), metadata)
  if client_options is None:
    client_options = ClientOptions(api_endpoint=regional_endpoint(subscription.location.region))
  assigner: Assigner
  if fixed_partitions:
    assigner = FixedSetAssigner(fixed_partitions)
  else:
    assignment_client = PartitionAssignmentServiceAsyncClient(credentials=credentials,
                                                              client_options=client_options)  # type: ignore
    assigner = _make_dynamic_assigner(subscription, assignment_client, metadata)

  subscribe_client = SubscriberServiceAsyncClient(credentials=credentials,
                                                  client_options=client_options)  # type: ignore
  cursor_client = CursorServiceAsyncClient(credentials=credentials, client_options=client_options)  # type: ignore
  if nack_handler is None:
    nack_handler = DefaultNackHandler()
  if message_transformer is None:
    message_transformer = DefaultMessageTransformer()
  partition_subscriber_factory = _make_partition_subscriber_factory(subscription, subscribe_client, cursor_client,
                                                                    metadata, per_partition_flow_control_settings,
                                                                    nack_handler, message_transformer)
  return AssigningSubscriber(assigner, partition_subscriber_factory)
