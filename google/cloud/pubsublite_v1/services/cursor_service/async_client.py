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

from google.cloud.pubsublite_v1.services.cursor_service import pagers
from google.cloud.pubsublite_v1.types import cursor

from .transports.base import CursorServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import CursorServiceGrpcAsyncIOTransport
from .client import CursorServiceClient


class CursorServiceAsyncClient:
    """The service that a subscriber client application uses to
    manage committed cursors while receiving messsages. A cursor
    represents a subscriber's progress within a topic partition for
    a given subscription.
    """

    _client: CursorServiceClient

    DEFAULT_ENDPOINT = CursorServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = CursorServiceClient.DEFAULT_MTLS_ENDPOINT

    subscription_path = staticmethod(CursorServiceClient.subscription_path)
    parse_subscription_path = staticmethod(CursorServiceClient.parse_subscription_path)

    common_billing_account_path = staticmethod(
        CursorServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        CursorServiceClient.parse_common_billing_account_path
    )

    common_folder_path = staticmethod(CursorServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        CursorServiceClient.parse_common_folder_path
    )

    common_organization_path = staticmethod(
        CursorServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        CursorServiceClient.parse_common_organization_path
    )

    common_project_path = staticmethod(CursorServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        CursorServiceClient.parse_common_project_path
    )

    common_location_path = staticmethod(CursorServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        CursorServiceClient.parse_common_location_path
    )

    @classmethod
    def from_service_account_info(cls, info: dict, *args, **kwargs):
        """Creates an instance of this client using the provided credentials info.

        Args:
            info (dict): The service account private key info.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            CursorServiceAsyncClient: The constructed client.
        """
        return CursorServiceClient.from_service_account_info.__func__(CursorServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            CursorServiceAsyncClient: The constructed client.
        """
        return CursorServiceClient.from_service_account_file.__func__(CursorServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> CursorServiceTransport:
        """Return the transport used by the client instance.

        Returns:
            CursorServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(CursorServiceClient).get_transport_class, type(CursorServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: credentials.Credentials = None,
        transport: Union[str, CursorServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiate the cursor service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.CursorServiceTransport]): The
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

        self._client = CursorServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    def streaming_commit_cursor(
        self,
        requests: AsyncIterator[cursor.StreamingCommitCursorRequest] = None,
        *,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> Awaitable[AsyncIterable[cursor.StreamingCommitCursorResponse]]:
        r"""Establishes a stream with the server for managing
        committed cursors.

        Args:
            requests (AsyncIterator[`google.cloud.pubsublite_v1.types.StreamingCommitCursorRequest`]):
                The request object AsyncIterator. A request sent from the client to
                the server on a stream.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            AsyncIterable[google.cloud.pubsublite_v1.types.StreamingCommitCursorResponse]:
                Response to a
                StreamingCommitCursorRequest.

        """

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.streaming_commit_cursor,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Send the request.
        response = rpc(requests, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def commit_cursor(
        self,
        request: cursor.CommitCursorRequest = None,
        *,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> cursor.CommitCursorResponse:
        r"""Updates the committed cursor.

        Args:
            request (:class:`google.cloud.pubsublite_v1.types.CommitCursorRequest`):
                The request object. Request for CommitCursor.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.pubsublite_v1.types.CommitCursorResponse:
                Response for CommitCursor.
        """
        # Create or coerce a protobuf request object.

        request = cursor.CommitCursorRequest(request)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.commit_cursor,
            default_retry=retries.Retry(
                initial=0.1,
                maximum=60.0,
                multiplier=1.3,
                predicate=retries.if_exception_type(
                    exceptions.Aborted,
                    exceptions.DeadlineExceeded,
                    exceptions.InternalServerError,
                    exceptions.ServiceUnavailable,
                    exceptions.Unknown,
                ),
                deadline=600.0,
            ),
            default_timeout=600.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def list_partition_cursors(
        self,
        request: cursor.ListPartitionCursorsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListPartitionCursorsAsyncPager:
        r"""Returns all committed cursor information for a
        subscription.

        Args:
            request (:class:`google.cloud.pubsublite_v1.types.ListPartitionCursorsRequest`):
                The request object. Request for ListPartitionCursors.
            parent (:class:`str`):
                Required. The subscription for which to retrieve
                cursors. Structured like
                ``projects/{project_number}/locations/{location}/subscriptions/{subscription_id}``.

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.pubsublite_v1.services.cursor_service.pagers.ListPartitionCursorsAsyncPager:
                Response for ListPartitionCursors
                Iterating over this object will yield
                results and resolve additional pages
                automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = cursor.ListPartitionCursorsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_partition_cursors,
            default_retry=retries.Retry(
                initial=0.1,
                maximum=60.0,
                multiplier=1.3,
                predicate=retries.if_exception_type(
                    exceptions.Aborted,
                    exceptions.DeadlineExceeded,
                    exceptions.InternalServerError,
                    exceptions.ServiceUnavailable,
                    exceptions.Unknown,
                ),
                deadline=600.0,
            ),
            default_timeout=600.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__aiter__` convenience method.
        response = pagers.ListPartitionCursorsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

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


__all__ = ("CursorServiceAsyncClient",)
