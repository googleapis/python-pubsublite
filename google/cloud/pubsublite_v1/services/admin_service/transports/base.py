# -*- coding: utf-8 -*-
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
#
import abc
from typing import Awaitable, Callable, Dict, Optional, Sequence, Union
import packaging.version
import pkg_resources

import google.auth  # type: ignore
import google.api_core  # type: ignore
from google.api_core import exceptions as core_exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.cloud.pubsublite_v1.types import admin
from google.cloud.pubsublite_v1.types import common
from google.longrunning import operations_pb2  # type: ignore
from google.protobuf import empty_pb2  # type: ignore

try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-pubsublite",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()

try:
    # google.auth.__version__ was added in 1.26.0
    _GOOGLE_AUTH_VERSION = google.auth.__version__
except AttributeError:
    try:  # try pkg_resources if it is available
        _GOOGLE_AUTH_VERSION = pkg_resources.get_distribution("google-auth").version
    except pkg_resources.DistributionNotFound:  # pragma: NO COVER
        _GOOGLE_AUTH_VERSION = None


class AdminServiceTransport(abc.ABC):
    """Abstract transport class for AdminService."""

    AUTH_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

    DEFAULT_HOST: str = "pubsublite.googleapis.com"

    def __init__(
        self,
        *,
        host: str = DEFAULT_HOST,
        credentials: ga_credentials.Credentials = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        always_use_jwt_access: Optional[bool] = False,
        **kwargs,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scopes (Optional[Sequence[str]]): A list of scopes.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

        scopes_kwargs = self._get_scopes_kwargs(self._host, scopes)

        # Save the scopes.
        self._scopes = scopes

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise core_exceptions.DuplicateCredentialArgs(
                "'credentials_file' and 'credentials' are mutually exclusive"
            )

        if credentials_file is not None:
            credentials, _ = google.auth.load_credentials_from_file(
                credentials_file, **scopes_kwargs, quota_project_id=quota_project_id
            )

        elif credentials is None:
            credentials, _ = google.auth.default(
                **scopes_kwargs, quota_project_id=quota_project_id
            )

        # If the credentials is service account credentials, then always try to use self signed JWT.
        if (
            always_use_jwt_access
            and isinstance(credentials, service_account.Credentials)
            and hasattr(service_account.Credentials, "with_always_use_jwt_access")
        ):
            credentials = credentials.with_always_use_jwt_access(True)

        # Save the credentials.
        self._credentials = credentials

    # TODO(busunkim): This method is in the base transport
    # to avoid duplicating code across the transport classes. These functions
    # should be deleted once the minimum required versions of google-auth is increased.

    # TODO: Remove this function once google-auth >= 1.25.0 is required
    @classmethod
    def _get_scopes_kwargs(
        cls, host: str, scopes: Optional[Sequence[str]]
    ) -> Dict[str, Optional[Sequence[str]]]:
        """Returns scopes kwargs to pass to google-auth methods depending on the google-auth version"""

        scopes_kwargs = {}

        if _GOOGLE_AUTH_VERSION and (
            packaging.version.parse(_GOOGLE_AUTH_VERSION)
            >= packaging.version.parse("1.25.0")
        ):
            scopes_kwargs = {"scopes": scopes, "default_scopes": cls.AUTH_SCOPES}
        else:
            scopes_kwargs = {"scopes": scopes or cls.AUTH_SCOPES}

        return scopes_kwargs

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.create_topic: gapic_v1.method.wrap_method(
                self.create_topic, default_timeout=None, client_info=client_info,
            ),
            self.get_topic: gapic_v1.method.wrap_method(
                self.get_topic, default_timeout=None, client_info=client_info,
            ),
            self.get_topic_partitions: gapic_v1.method.wrap_method(
                self.get_topic_partitions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_topics: gapic_v1.method.wrap_method(
                self.list_topics, default_timeout=None, client_info=client_info,
            ),
            self.update_topic: gapic_v1.method.wrap_method(
                self.update_topic, default_timeout=None, client_info=client_info,
            ),
            self.delete_topic: gapic_v1.method.wrap_method(
                self.delete_topic, default_timeout=None, client_info=client_info,
            ),
            self.list_topic_subscriptions: gapic_v1.method.wrap_method(
                self.list_topic_subscriptions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_subscription: gapic_v1.method.wrap_method(
                self.create_subscription, default_timeout=None, client_info=client_info,
            ),
            self.get_subscription: gapic_v1.method.wrap_method(
                self.get_subscription, default_timeout=None, client_info=client_info,
            ),
            self.list_subscriptions: gapic_v1.method.wrap_method(
                self.list_subscriptions, default_timeout=None, client_info=client_info,
            ),
            self.update_subscription: gapic_v1.method.wrap_method(
                self.update_subscription, default_timeout=None, client_info=client_info,
            ),
            self.delete_subscription: gapic_v1.method.wrap_method(
                self.delete_subscription, default_timeout=None, client_info=client_info,
            ),
            self.seek_subscription: gapic_v1.method.wrap_method(
                self.seek_subscription, default_timeout=None, client_info=client_info,
            ),
            self.create_reservation: gapic_v1.method.wrap_method(
                self.create_reservation, default_timeout=None, client_info=client_info,
            ),
            self.get_reservation: gapic_v1.method.wrap_method(
                self.get_reservation, default_timeout=None, client_info=client_info,
            ),
            self.list_reservations: gapic_v1.method.wrap_method(
                self.list_reservations, default_timeout=None, client_info=client_info,
            ),
            self.update_reservation: gapic_v1.method.wrap_method(
                self.update_reservation, default_timeout=None, client_info=client_info,
            ),
            self.delete_reservation: gapic_v1.method.wrap_method(
                self.delete_reservation, default_timeout=None, client_info=client_info,
            ),
            self.list_reservation_topics: gapic_v1.method.wrap_method(
                self.list_reservation_topics,
                default_timeout=None,
                client_info=client_info,
            ),
        }

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def create_topic(
        self,
    ) -> Callable[
        [admin.CreateTopicRequest], Union[common.Topic, Awaitable[common.Topic]]
    ]:
        raise NotImplementedError()

    @property
    def get_topic(
        self,
    ) -> Callable[
        [admin.GetTopicRequest], Union[common.Topic, Awaitable[common.Topic]]
    ]:
        raise NotImplementedError()

    @property
    def get_topic_partitions(
        self,
    ) -> Callable[
        [admin.GetTopicPartitionsRequest],
        Union[admin.TopicPartitions, Awaitable[admin.TopicPartitions]],
    ]:
        raise NotImplementedError()

    @property
    def list_topics(
        self,
    ) -> Callable[
        [admin.ListTopicsRequest],
        Union[admin.ListTopicsResponse, Awaitable[admin.ListTopicsResponse]],
    ]:
        raise NotImplementedError()

    @property
    def update_topic(
        self,
    ) -> Callable[
        [admin.UpdateTopicRequest], Union[common.Topic, Awaitable[common.Topic]]
    ]:
        raise NotImplementedError()

    @property
    def delete_topic(
        self,
    ) -> Callable[
        [admin.DeleteTopicRequest], Union[empty_pb2.Empty, Awaitable[empty_pb2.Empty]]
    ]:
        raise NotImplementedError()

    @property
    def list_topic_subscriptions(
        self,
    ) -> Callable[
        [admin.ListTopicSubscriptionsRequest],
        Union[
            admin.ListTopicSubscriptionsResponse,
            Awaitable[admin.ListTopicSubscriptionsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def create_subscription(
        self,
    ) -> Callable[
        [admin.CreateSubscriptionRequest],
        Union[common.Subscription, Awaitable[common.Subscription]],
    ]:
        raise NotImplementedError()

    @property
    def get_subscription(
        self,
    ) -> Callable[
        [admin.GetSubscriptionRequest],
        Union[common.Subscription, Awaitable[common.Subscription]],
    ]:
        raise NotImplementedError()

    @property
    def list_subscriptions(
        self,
    ) -> Callable[
        [admin.ListSubscriptionsRequest],
        Union[
            admin.ListSubscriptionsResponse, Awaitable[admin.ListSubscriptionsResponse]
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_subscription(
        self,
    ) -> Callable[
        [admin.UpdateSubscriptionRequest],
        Union[common.Subscription, Awaitable[common.Subscription]],
    ]:
        raise NotImplementedError()

    @property
    def delete_subscription(
        self,
    ) -> Callable[
        [admin.DeleteSubscriptionRequest],
        Union[empty_pb2.Empty, Awaitable[empty_pb2.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def seek_subscription(
        self,
    ) -> Callable[
        [admin.SeekSubscriptionRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def create_reservation(
        self,
    ) -> Callable[
        [admin.CreateReservationRequest],
        Union[common.Reservation, Awaitable[common.Reservation]],
    ]:
        raise NotImplementedError()

    @property
    def get_reservation(
        self,
    ) -> Callable[
        [admin.GetReservationRequest],
        Union[common.Reservation, Awaitable[common.Reservation]],
    ]:
        raise NotImplementedError()

    @property
    def list_reservations(
        self,
    ) -> Callable[
        [admin.ListReservationsRequest],
        Union[
            admin.ListReservationsResponse, Awaitable[admin.ListReservationsResponse]
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_reservation(
        self,
    ) -> Callable[
        [admin.UpdateReservationRequest],
        Union[common.Reservation, Awaitable[common.Reservation]],
    ]:
        raise NotImplementedError()

    @property
    def delete_reservation(
        self,
    ) -> Callable[
        [admin.DeleteReservationRequest],
        Union[empty_pb2.Empty, Awaitable[empty_pb2.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def list_reservation_topics(
        self,
    ) -> Callable[
        [admin.ListReservationTopicsRequest],
        Union[
            admin.ListReservationTopicsResponse,
            Awaitable[admin.ListReservationTopicsResponse],
        ],
    ]:
        raise NotImplementedError()


__all__ = ("AdminServiceTransport",)
