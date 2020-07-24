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
from typing import Dict, AsyncIterable, AsyncIterator, Sequence, Tuple, Type, Union
import pkg_resources

import google.api_core.client_options as ClientOptions  # type: ignore
from google.api_core import exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.auth import credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.cloud.pubsublite_v1.types import subscriber

from .transports.base import PartitionAssignmentServiceTransport
from .transports.grpc_asyncio import PartitionAssignmentServiceGrpcAsyncIOTransport
from .client import PartitionAssignmentServiceClient


class PartitionAssignmentServiceAsyncClient:
    """The service that a subscriber client application uses to
    determine which partitions it should connect to.

    This is an under development API being published to build client
    libraries. Users will not be able to access it until fully
    launched.
    """

    _client: PartitionAssignmentServiceClient

    DEFAULT_ENDPOINT = PartitionAssignmentServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = PartitionAssignmentServiceClient.DEFAULT_MTLS_ENDPOINT

    from_service_account_file = (
        PartitionAssignmentServiceClient.from_service_account_file
    )
    from_service_account_json = from_service_account_file

    get_transport_class = functools.partial(
        type(PartitionAssignmentServiceClient).get_transport_class,
        type(PartitionAssignmentServiceClient),
    )

    def __init__(
        self,
        *,
        credentials: credentials.Credentials = None,
        transport: Union[str, PartitionAssignmentServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
    ) -> None:
        """Instantiate the partition assignment service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.PartitionAssignmentServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (ClientOptions): Custom options for the client. It
                won't take effect if a ``transport`` instance is provided.
                (1) The ``api_endpoint`` property can be used to override the
                default endpoint provided by the client. GOOGLE_API_USE_MTLS
                environment variable can also be used to override the endpoint:
                "always" (always use the default mTLS endpoint), "never" (always
                use the default regular endpoint, this is the default value for
                the environment variable) and "auto" (auto switch to the default
                mTLS endpoint if client SSL credentials is present). However,
                the ``api_endpoint`` property takes precedence if provided.
                (2) The ``client_cert_source`` property is used to provide client
                SSL credentials for mutual TLS transport. If not provided, the
                default SSL credentials will be used if present.

        Raises:
            google.auth.exceptions.MutualTlsChannelError: If mutual TLS transport
                creation failed for any reason.
        """

        self._client = PartitionAssignmentServiceClient(
            credentials=credentials, transport=transport, client_options=client_options,
        )

    def assign_partitions(
        self,
        requests: AsyncIterator[subscriber.PartitionAssignmentRequest] = None,
        *,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> AsyncIterable[subscriber.PartitionAssignment]:
        r"""Assign partitions for this client to handle for the
        specified subscription.
        The client must send an
        InitialPartitionAssignmentRequest first. The server will
        then send at most one unacknowledged PartitionAssignment
        outstanding on the stream at a time.
        The client should send a PartitionAssignmentAck after
        updating the partitions it is connected to to reflect
        the new assignment.

        Args:
            requests (AsyncIterator[`~.subscriber.PartitionAssignmentRequest`]):
                The request object AsyncIterator. A request on the PartitionAssignment
                stream.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            AsyncIterable[~.subscriber.PartitionAssignment]:
                PartitionAssignments should not race
                with acknowledgements. There should be
                exactly one unacknowledged
                PartitionAssignment at a time. If not,
                the client must break the stream.

        """

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.assign_partitions,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(requests, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response


try:
    _client_info = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-pubsublite",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    _client_info = gapic_v1.client_info.ClientInfo()


__all__ = ("PartitionAssignmentServiceAsyncClient",)
