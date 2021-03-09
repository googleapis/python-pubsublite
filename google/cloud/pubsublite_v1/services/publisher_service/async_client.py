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

from collections import OrderedDict
import functools
import re
from typing import (
    Dict,
    AsyncIterable,
    Awaitable,
    AsyncIterator,
    Sequence,
    Tuple,
    Type,
    Union,
)
import pkg_resources

import google.api_core.client_options as ClientOptions  # type: ignore
from google.api_core import exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.auth import credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.cloud.pubsublite_v1.types import publisher

from .transports.base import PublisherServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import PublisherServiceGrpcAsyncIOTransport
from .client import PublisherServiceClient


class PublisherServiceAsyncClient:
    """The service that a publisher client application uses to publish
    messages to topics. Published messages are retained by the service
    for the duration of the retention period configured for the
    respective topic, and are delivered to subscriber clients upon
    request (via the ``SubscriberService``).
    """

    _client: PublisherServiceClient

    DEFAULT_ENDPOINT = PublisherServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = PublisherServiceClient.DEFAULT_MTLS_ENDPOINT

    common_billing_account_path = staticmethod(
        PublisherServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        PublisherServiceClient.parse_common_billing_account_path
    )

    common_folder_path = staticmethod(PublisherServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        PublisherServiceClient.parse_common_folder_path
    )

    common_organization_path = staticmethod(
        PublisherServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        PublisherServiceClient.parse_common_organization_path
    )

    common_project_path = staticmethod(PublisherServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        PublisherServiceClient.parse_common_project_path
    )

    common_location_path = staticmethod(PublisherServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        PublisherServiceClient.parse_common_location_path
    )

    @classmethod
    def from_service_account_info(cls, info: dict, *args, **kwargs):
        """Creates an instance of this client using the provided credentials info.

        Args:
            info (dict): The service account private key info.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            PublisherServiceAsyncClient: The constructed client.
        """
        return PublisherServiceClient.from_service_account_info.__func__(PublisherServiceAsyncClient, info, *args, **kwargs)  # type: ignore

    @classmethod
    def from_service_account_file(cls, filename: str, *args, **kwargs):
        """Creates an instance of this client using the provided credentials
        file.

        Args:
            filename (str): The path to the service account private key json
                file.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            PublisherServiceAsyncClient: The constructed client.
        """
        return PublisherServiceClient.from_service_account_file.__func__(PublisherServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> PublisherServiceTransport:
        """Return the transport used by the client instance.

        Returns:
            PublisherServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(PublisherServiceClient).get_transport_class, type(PublisherServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: credentials.Credentials = None,
        transport: Union[str, PublisherServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiate the publisher service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.PublisherServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (ClientOptions): Custom options for the client. It
                won't take effect if a ``transport`` instance is provided.
                (1) The ``api_endpoint`` property can be used to override the
                default endpoint provided by the client. GOOGLE_API_USE_MTLS_ENDPOINT
                environment variable can also be used to override the endpoint:
                "always" (always use the default mTLS endpoint), "never" (always
                use the default regular endpoint) and "auto" (auto switch to the
                default mTLS endpoint if client certificate is present, this is
                the default value). However, the ``api_endpoint`` property takes
                precedence if provided.
                (2) If GOOGLE_API_USE_CLIENT_CERTIFICATE environment variable
                is "true", then the ``client_cert_source`` property can be used
                to provide client certificate for mutual TLS transport. If
                not provided, the default SSL client certificate will be used if
                present. If GOOGLE_API_USE_CLIENT_CERTIFICATE is "false" or not
                set, no client certificate will be used.

        Raises:
            google.auth.exceptions.MutualTlsChannelError: If mutual TLS transport
                creation failed for any reason.
        """

        self._client = PublisherServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    def publish(
        self,
        requests: AsyncIterator[publisher.PublishRequest] = None,
        *,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> Awaitable[AsyncIterable[publisher.PublishResponse]]:
        r"""Establishes a stream with the server for publishing
        messages. Once the stream is initialized, the client
        publishes messages by sending publish requests on the
        stream. The server responds with a PublishResponse for
        each PublishRequest sent by the client, in the same
        order that the requests were sent. Note that multiple
        PublishRequests can be in flight simultaneously, but
        they will be processed by the server in the order that
        they are sent by the client on a given stream.

        Args:
            requests (AsyncIterator[`google.cloud.pubsublite_v1.types.PublishRequest`]):
                The request object AsyncIterator. Request sent from the client to the
                server on a stream.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            AsyncIterable[google.cloud.pubsublite_v1.types.PublishResponse]:
                Response to a PublishRequest.
        """

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.publish,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Send the request.
        response = rpc(requests, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-pubsublite",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()


__all__ = ("PublisherServiceAsyncClient",)
