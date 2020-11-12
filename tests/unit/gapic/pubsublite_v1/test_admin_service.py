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

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.pubsublite_v1.services.admin_service import AdminServiceAsyncClient
from google.cloud.pubsublite_v1.services.admin_service import AdminServiceClient
from google.cloud.pubsublite_v1.services.admin_service import pagers
from google.cloud.pubsublite_v1.services.admin_service import transports
from google.cloud.pubsublite_v1.types import admin
from google.cloud.pubsublite_v1.types import common
from google.oauth2 import service_account
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert AdminServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        AdminServiceClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    )
    assert (
        AdminServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        AdminServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        AdminServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert AdminServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize("client_class", [AdminServiceClient, AdminServiceAsyncClient])
def test_admin_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds

        assert client.transport._host == "pubsublite.googleapis.com:443"


def test_admin_service_client_get_transport_class():
    transport = AdminServiceClient.get_transport_class()
    assert transport == transports.AdminServiceGrpcTransport

    transport = AdminServiceClient.get_transport_class("grpc")
    assert transport == transports.AdminServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc"),
        (
            AdminServiceAsyncClient,
            transports.AdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    AdminServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AdminServiceClient)
)
@mock.patch.object(
    AdminServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(AdminServiceAsyncClient),
)
def test_admin_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(AdminServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(AdminServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc", "true"),
        (
            AdminServiceAsyncClient,
            transports.AdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc", "false"),
        (
            AdminServiceAsyncClient,
            transports.AdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    AdminServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AdminServiceClient)
)
@mock.patch.object(
    AdminServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(AdminServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_admin_service_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            ssl_channel_creds = mock.Mock()
            with mock.patch(
                "grpc.ssl_channel_credentials", return_value=ssl_channel_creds
            ):
                patched.return_value = None
                client = client_class(client_options=options)

                if use_client_cert_env == "false":
                    expected_ssl_channel_creds = None
                    expected_host = client.DEFAULT_ENDPOINT
                else:
                    expected_ssl_channel_creds = ssl_channel_creds
                    expected_host = client.DEFAULT_MTLS_ENDPOINT

                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=expected_host,
                    scopes=None,
                    ssl_channel_credentials=expected_ssl_channel_creds,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    with mock.patch(
                        "google.auth.transport.grpc.SslCredentials.ssl_credentials",
                        new_callable=mock.PropertyMock,
                    ) as ssl_credentials_mock:
                        if use_client_cert_env == "false":
                            is_mtls_mock.return_value = False
                            ssl_credentials_mock.return_value = None
                            expected_host = client.DEFAULT_ENDPOINT
                            expected_ssl_channel_creds = None
                        else:
                            is_mtls_mock.return_value = True
                            ssl_credentials_mock.return_value = mock.Mock()
                            expected_host = client.DEFAULT_MTLS_ENDPOINT
                            expected_ssl_channel_creds = (
                                ssl_credentials_mock.return_value
                            )

                        patched.return_value = None
                        client = client_class()
                        patched.assert_called_once_with(
                            credentials=None,
                            credentials_file=None,
                            host=expected_host,
                            scopes=None,
                            ssl_channel_credentials=expected_ssl_channel_creds,
                            quota_project_id=None,
                            client_info=transports.base.DEFAULT_CLIENT_INFO,
                        )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    is_mtls_mock.return_value = False
                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=client.DEFAULT_ENDPOINT,
                        scopes=None,
                        ssl_channel_credentials=None,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc"),
        (
            AdminServiceAsyncClient,
            transports.AdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_admin_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc"),
        (
            AdminServiceAsyncClient,
            transports.AdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_admin_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_admin_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = AdminServiceClient(client_options={"api_endpoint": "squid.clam.whelk"})
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_create_topic(transport: str = "grpc", request_type=admin.CreateTopicRequest):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic(name="name_value",)

        response = client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.CreateTopicRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, common.Topic)

    assert response.name == "name_value"


def test_create_topic_from_dict():
    test_create_topic(request_type=dict)


@pytest.mark.asyncio
async def test_create_topic_async(
    transport: str = "grpc_asyncio", request_type=admin.CreateTopicRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            common.Topic(name="name_value",)
        )

        response = await client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.CreateTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)

    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_create_topic_async_from_dict():
    await test_create_topic_async(request_type=dict)


def test_create_topic_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateTopicRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_topic), "__call__") as call:
        call.return_value = common.Topic()

        client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_topic_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateTopicRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_topic), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())

        await client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_topic_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_topic(
            parent="parent_value",
            topic=common.Topic(name="name_value"),
            topic_id="topic_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].topic == common.Topic(name="name_value")

        assert args[0].topic_id == "topic_id_value"


def test_create_topic_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_topic(
            admin.CreateTopicRequest(),
            parent="parent_value",
            topic=common.Topic(name="name_value"),
            topic_id="topic_id_value",
        )


@pytest.mark.asyncio
async def test_create_topic_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_topic(
            parent="parent_value",
            topic=common.Topic(name="name_value"),
            topic_id="topic_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].topic == common.Topic(name="name_value")

        assert args[0].topic_id == "topic_id_value"


@pytest.mark.asyncio
async def test_create_topic_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_topic(
            admin.CreateTopicRequest(),
            parent="parent_value",
            topic=common.Topic(name="name_value"),
            topic_id="topic_id_value",
        )


def test_get_topic(transport: str = "grpc", request_type=admin.GetTopicRequest):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic(name="name_value",)

        response = client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.GetTopicRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, common.Topic)

    assert response.name == "name_value"


def test_get_topic_from_dict():
    test_get_topic(request_type=dict)


@pytest.mark.asyncio
async def test_get_topic_async(
    transport: str = "grpc_asyncio", request_type=admin.GetTopicRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            common.Topic(name="name_value",)
        )

        response = await client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.GetTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)

    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_get_topic_async_from_dict():
    await test_get_topic_async(request_type=dict)


def test_get_topic_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_topic), "__call__") as call:
        call.return_value = common.Topic()

        client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_topic_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_topic), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())

        await client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_topic_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_topic(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_topic_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_topic(
            admin.GetTopicRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_topic_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_topic(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_topic_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_topic(
            admin.GetTopicRequest(), name="name_value",
        )


def test_get_topic_partitions(
    transport: str = "grpc", request_type=admin.GetTopicPartitionsRequest
):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_topic_partitions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.TopicPartitions(partition_count=1634,)

        response = client.get_topic_partitions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.GetTopicPartitionsRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, admin.TopicPartitions)

    assert response.partition_count == 1634


def test_get_topic_partitions_from_dict():
    test_get_topic_partitions(request_type=dict)


@pytest.mark.asyncio
async def test_get_topic_partitions_async(
    transport: str = "grpc_asyncio", request_type=admin.GetTopicPartitionsRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_topic_partitions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.TopicPartitions(partition_count=1634,)
        )

        response = await client.get_topic_partitions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.GetTopicPartitionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, admin.TopicPartitions)

    assert response.partition_count == 1634


@pytest.mark.asyncio
async def test_get_topic_partitions_async_from_dict():
    await test_get_topic_partitions_async(request_type=dict)


def test_get_topic_partitions_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicPartitionsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_topic_partitions), "__call__"
    ) as call:
        call.return_value = admin.TopicPartitions()

        client.get_topic_partitions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_topic_partitions_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicPartitionsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_topic_partitions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.TopicPartitions()
        )

        await client.get_topic_partitions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_topic_partitions_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_topic_partitions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.TopicPartitions()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_topic_partitions(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_topic_partitions_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_topic_partitions(
            admin.GetTopicPartitionsRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_topic_partitions_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_topic_partitions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.TopicPartitions()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.TopicPartitions()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_topic_partitions(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_topic_partitions_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_topic_partitions(
            admin.GetTopicPartitionsRequest(), name="name_value",
        )


def test_list_topics(transport: str = "grpc", request_type=admin.ListTopicsRequest):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.ListTopicsRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListTopicsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_topics_from_dict():
    test_list_topics(request_type=dict)


@pytest.mark.asyncio
async def test_list_topics_async(
    transport: str = "grpc_asyncio", request_type=admin.ListTopicsRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListTopicsResponse(next_page_token="next_page_token_value",)
        )

        response = await client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.ListTopicsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTopicsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_topics_async_from_dict():
    await test_list_topics_async(request_type=dict)


def test_list_topics_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        call.return_value = admin.ListTopicsResponse()

        client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_topics_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListTopicsResponse()
        )

        await client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_topics_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_topics(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_topics_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_topics(
            admin.ListTopicsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_topics_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListTopicsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_topics(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_topics_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_topics(
            admin.ListTopicsRequest(), parent="parent_value",
        )


def test_list_topics_pager():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[common.Topic(), common.Topic(), common.Topic(),],
                next_page_token="abc",
            ),
            admin.ListTopicsResponse(topics=[], next_page_token="def",),
            admin.ListTopicsResponse(topics=[common.Topic(),], next_page_token="ghi",),
            admin.ListTopicsResponse(topics=[common.Topic(), common.Topic(),],),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_topics(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, common.Topic) for i in results)


def test_list_topics_pages():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_topics), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[common.Topic(), common.Topic(), common.Topic(),],
                next_page_token="abc",
            ),
            admin.ListTopicsResponse(topics=[], next_page_token="def",),
            admin.ListTopicsResponse(topics=[common.Topic(),], next_page_token="ghi",),
            admin.ListTopicsResponse(topics=[common.Topic(), common.Topic(),],),
            RuntimeError,
        )
        pages = list(client.list_topics(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_topics_async_pager():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topics), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[common.Topic(), common.Topic(), common.Topic(),],
                next_page_token="abc",
            ),
            admin.ListTopicsResponse(topics=[], next_page_token="def",),
            admin.ListTopicsResponse(topics=[common.Topic(),], next_page_token="ghi",),
            admin.ListTopicsResponse(topics=[common.Topic(), common.Topic(),],),
            RuntimeError,
        )
        async_pager = await client.list_topics(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, common.Topic) for i in responses)


@pytest.mark.asyncio
async def test_list_topics_async_pages():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topics), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[common.Topic(), common.Topic(), common.Topic(),],
                next_page_token="abc",
            ),
            admin.ListTopicsResponse(topics=[], next_page_token="def",),
            admin.ListTopicsResponse(topics=[common.Topic(),], next_page_token="ghi",),
            admin.ListTopicsResponse(topics=[common.Topic(), common.Topic(),],),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_topics(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_topic(transport: str = "grpc", request_type=admin.UpdateTopicRequest):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic(name="name_value",)

        response = client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.UpdateTopicRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, common.Topic)

    assert response.name == "name_value"


def test_update_topic_from_dict():
    test_update_topic(request_type=dict)


@pytest.mark.asyncio
async def test_update_topic_async(
    transport: str = "grpc_asyncio", request_type=admin.UpdateTopicRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            common.Topic(name="name_value",)
        )

        response = await client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.UpdateTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)

    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_update_topic_async_from_dict():
    await test_update_topic_async(request_type=dict)


def test_update_topic_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateTopicRequest()
    request.topic.name = "topic.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_topic), "__call__") as call:
        call.return_value = common.Topic()

        client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "topic.name=topic.name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_topic_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateTopicRequest()
    request.topic.name = "topic.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_topic), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())

        await client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "topic.name=topic.name/value",) in kw["metadata"]


def test_update_topic_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_topic(
            topic=common.Topic(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].topic == common.Topic(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_topic_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_topic(
            admin.UpdateTopicRequest(),
            topic=common.Topic(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_topic_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_topic(
            topic=common.Topic(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].topic == common.Topic(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_topic_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_topic(
            admin.UpdateTopicRequest(),
            topic=common.Topic(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_delete_topic(transport: str = "grpc", request_type=admin.DeleteTopicRequest):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.DeleteTopicRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_topic_from_dict():
    test_delete_topic(request_type=dict)


@pytest.mark.asyncio
async def test_delete_topic_async(
    transport: str = "grpc_asyncio", request_type=admin.DeleteTopicRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.DeleteTopicRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_topic_async_from_dict():
    await test_delete_topic_async(request_type=dict)


def test_delete_topic_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteTopicRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_topic), "__call__") as call:
        call.return_value = None

        client.delete_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_topic_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteTopicRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_topic), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_topic_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_topic(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_topic_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_topic(
            admin.DeleteTopicRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_topic_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_topic), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_topic(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_topic_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_topic(
            admin.DeleteTopicRequest(), name="name_value",
        )


def test_list_topic_subscriptions(
    transport: str = "grpc", request_type=admin.ListTopicSubscriptionsRequest
):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicSubscriptionsResponse(
            subscriptions=["subscriptions_value"],
            next_page_token="next_page_token_value",
        )

        response = client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.ListTopicSubscriptionsRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListTopicSubscriptionsPager)

    assert response.subscriptions == ["subscriptions_value"]

    assert response.next_page_token == "next_page_token_value"


def test_list_topic_subscriptions_from_dict():
    test_list_topic_subscriptions(request_type=dict)


@pytest.mark.asyncio
async def test_list_topic_subscriptions_async(
    transport: str = "grpc_asyncio", request_type=admin.ListTopicSubscriptionsRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListTopicSubscriptionsResponse(
                subscriptions=["subscriptions_value"],
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.ListTopicSubscriptionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTopicSubscriptionsAsyncPager)

    assert response.subscriptions == ["subscriptions_value"]

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_topic_subscriptions_async_from_dict():
    await test_list_topic_subscriptions_async(request_type=dict)


def test_list_topic_subscriptions_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicSubscriptionsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        call.return_value = admin.ListTopicSubscriptionsResponse()

        client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_topic_subscriptions_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicSubscriptionsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListTopicSubscriptionsResponse()
        )

        await client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_list_topic_subscriptions_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicSubscriptionsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_topic_subscriptions(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_list_topic_subscriptions_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_topic_subscriptions(
            admin.ListTopicSubscriptionsRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_list_topic_subscriptions_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicSubscriptionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListTopicSubscriptionsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_topic_subscriptions(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_list_topic_subscriptions_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_topic_subscriptions(
            admin.ListTopicSubscriptionsRequest(), name="name_value",
        )


def test_list_topic_subscriptions_pager():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(), str(), str(),], next_page_token="abc",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[], next_page_token="def",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(),], next_page_token="ghi",
            ),
            admin.ListTopicSubscriptionsResponse(subscriptions=[str(), str(),],),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", ""),)),
        )
        pager = client.list_topic_subscriptions(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, str) for i in results)


def test_list_topic_subscriptions_pages():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(), str(), str(),], next_page_token="abc",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[], next_page_token="def",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(),], next_page_token="ghi",
            ),
            admin.ListTopicSubscriptionsResponse(subscriptions=[str(), str(),],),
            RuntimeError,
        )
        pages = list(client.list_topic_subscriptions(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_topic_subscriptions_async_pager():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(), str(), str(),], next_page_token="abc",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[], next_page_token="def",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(),], next_page_token="ghi",
            ),
            admin.ListTopicSubscriptionsResponse(subscriptions=[str(), str(),],),
            RuntimeError,
        )
        async_pager = await client.list_topic_subscriptions(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, str) for i in responses)


@pytest.mark.asyncio
async def test_list_topic_subscriptions_async_pages():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_topic_subscriptions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(), str(), str(),], next_page_token="abc",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[], next_page_token="def",
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[str(),], next_page_token="ghi",
            ),
            admin.ListTopicSubscriptionsResponse(subscriptions=[str(), str(),],),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_topic_subscriptions(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_create_subscription(
    transport: str = "grpc", request_type=admin.CreateSubscriptionRequest
):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription(name="name_value", topic="topic_value",)

        response = client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.CreateSubscriptionRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, common.Subscription)

    assert response.name == "name_value"

    assert response.topic == "topic_value"


def test_create_subscription_from_dict():
    test_create_subscription(request_type=dict)


@pytest.mark.asyncio
async def test_create_subscription_async(
    transport: str = "grpc_asyncio", request_type=admin.CreateSubscriptionRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            common.Subscription(name="name_value", topic="topic_value",)
        )

        response = await client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.CreateSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)

    assert response.name == "name_value"

    assert response.topic == "topic_value"


@pytest.mark.asyncio
async def test_create_subscription_async_from_dict():
    await test_create_subscription_async(request_type=dict)


def test_create_subscription_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateSubscriptionRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_subscription), "__call__"
    ) as call:
        call.return_value = common.Subscription()

        client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_subscription_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateSubscriptionRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_subscription), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())

        await client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_subscription_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_subscription(
            parent="parent_value",
            subscription=common.Subscription(name="name_value"),
            subscription_id="subscription_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].subscription == common.Subscription(name="name_value")

        assert args[0].subscription_id == "subscription_id_value"


def test_create_subscription_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_subscription(
            admin.CreateSubscriptionRequest(),
            parent="parent_value",
            subscription=common.Subscription(name="name_value"),
            subscription_id="subscription_id_value",
        )


@pytest.mark.asyncio
async def test_create_subscription_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_subscription(
            parent="parent_value",
            subscription=common.Subscription(name="name_value"),
            subscription_id="subscription_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].subscription == common.Subscription(name="name_value")

        assert args[0].subscription_id == "subscription_id_value"


@pytest.mark.asyncio
async def test_create_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_subscription(
            admin.CreateSubscriptionRequest(),
            parent="parent_value",
            subscription=common.Subscription(name="name_value"),
            subscription_id="subscription_id_value",
        )


def test_get_subscription(
    transport: str = "grpc", request_type=admin.GetSubscriptionRequest
):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_subscription), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription(name="name_value", topic="topic_value",)

        response = client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.GetSubscriptionRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, common.Subscription)

    assert response.name == "name_value"

    assert response.topic == "topic_value"


def test_get_subscription_from_dict():
    test_get_subscription(request_type=dict)


@pytest.mark.asyncio
async def test_get_subscription_async(
    transport: str = "grpc_asyncio", request_type=admin.GetSubscriptionRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_subscription), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            common.Subscription(name="name_value", topic="topic_value",)
        )

        response = await client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.GetSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)

    assert response.name == "name_value"

    assert response.topic == "topic_value"


@pytest.mark.asyncio
async def test_get_subscription_async_from_dict():
    await test_get_subscription_async(request_type=dict)


def test_get_subscription_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetSubscriptionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_subscription), "__call__") as call:
        call.return_value = common.Subscription()

        client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_subscription_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetSubscriptionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_subscription), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())

        await client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_subscription_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_subscription), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_subscription(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_subscription_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_subscription(
            admin.GetSubscriptionRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_subscription_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_subscription), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_subscription(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_subscription(
            admin.GetSubscriptionRequest(), name="name_value",
        )


def test_list_subscriptions(
    transport: str = "grpc", request_type=admin.ListSubscriptionsRequest
):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListSubscriptionsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.ListSubscriptionsRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListSubscriptionsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_subscriptions_from_dict():
    test_list_subscriptions(request_type=dict)


@pytest.mark.asyncio
async def test_list_subscriptions_async(
    transport: str = "grpc_asyncio", request_type=admin.ListSubscriptionsRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListSubscriptionsResponse(next_page_token="next_page_token_value",)
        )

        response = await client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.ListSubscriptionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSubscriptionsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_subscriptions_async_from_dict():
    await test_list_subscriptions_async(request_type=dict)


def test_list_subscriptions_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListSubscriptionsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        call.return_value = admin.ListSubscriptionsResponse()

        client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_subscriptions_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListSubscriptionsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListSubscriptionsResponse()
        )

        await client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_subscriptions_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListSubscriptionsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_subscriptions(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_subscriptions_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_subscriptions(
            admin.ListSubscriptionsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_subscriptions_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListSubscriptionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            admin.ListSubscriptionsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_subscriptions(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_subscriptions_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_subscriptions(
            admin.ListSubscriptionsRequest(), parent="parent_value",
        )


def test_list_subscriptions_pager():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token="abc",
            ),
            admin.ListSubscriptionsResponse(subscriptions=[], next_page_token="def",),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(),], next_page_token="ghi",
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(), common.Subscription(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_subscriptions(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, common.Subscription) for i in results)


def test_list_subscriptions_pages():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token="abc",
            ),
            admin.ListSubscriptionsResponse(subscriptions=[], next_page_token="def",),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(),], next_page_token="ghi",
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(), common.Subscription(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_subscriptions(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_subscriptions_async_pager():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token="abc",
            ),
            admin.ListSubscriptionsResponse(subscriptions=[], next_page_token="def",),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(),], next_page_token="ghi",
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(), common.Subscription(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_subscriptions(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, common.Subscription) for i in responses)


@pytest.mark.asyncio
async def test_list_subscriptions_async_pages():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_subscriptions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token="abc",
            ),
            admin.ListSubscriptionsResponse(subscriptions=[], next_page_token="def",),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(),], next_page_token="ghi",
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[common.Subscription(), common.Subscription(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_subscriptions(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_subscription(
    transport: str = "grpc", request_type=admin.UpdateSubscriptionRequest
):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription(name="name_value", topic="topic_value",)

        response = client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.UpdateSubscriptionRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, common.Subscription)

    assert response.name == "name_value"

    assert response.topic == "topic_value"


def test_update_subscription_from_dict():
    test_update_subscription(request_type=dict)


@pytest.mark.asyncio
async def test_update_subscription_async(
    transport: str = "grpc_asyncio", request_type=admin.UpdateSubscriptionRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            common.Subscription(name="name_value", topic="topic_value",)
        )

        response = await client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.UpdateSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)

    assert response.name == "name_value"

    assert response.topic == "topic_value"


@pytest.mark.asyncio
async def test_update_subscription_async_from_dict():
    await test_update_subscription_async(request_type=dict)


def test_update_subscription_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateSubscriptionRequest()
    request.subscription.name = "subscription.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_subscription), "__call__"
    ) as call:
        call.return_value = common.Subscription()

        client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "subscription.name=subscription.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_subscription_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateSubscriptionRequest()
    request.subscription.name = "subscription.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_subscription), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())

        await client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "subscription.name=subscription.name/value",
    ) in kw["metadata"]


def test_update_subscription_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_subscription(
            subscription=common.Subscription(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].subscription == common.Subscription(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_subscription_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_subscription(
            admin.UpdateSubscriptionRequest(),
            subscription=common.Subscription(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_subscription_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_subscription(
            subscription=common.Subscription(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].subscription == common.Subscription(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_subscription(
            admin.UpdateSubscriptionRequest(),
            subscription=common.Subscription(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_delete_subscription(
    transport: str = "grpc", request_type=admin.DeleteSubscriptionRequest
):
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.DeleteSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_subscription_from_dict():
    test_delete_subscription(request_type=dict)


@pytest.mark.asyncio
async def test_delete_subscription_async(
    transport: str = "grpc_asyncio", request_type=admin.DeleteSubscriptionRequest
):
    client = AdminServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == admin.DeleteSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_subscription_async_from_dict():
    await test_delete_subscription_async(request_type=dict)


def test_delete_subscription_field_headers():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteSubscriptionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_subscription), "__call__"
    ) as call:
        call.return_value = None

        client.delete_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_subscription_field_headers_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteSubscriptionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_subscription), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_subscription_flattened():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_subscription(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_subscription_flattened_error():
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_subscription(
            admin.DeleteSubscriptionRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_subscription_flattened_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_subscription), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_subscription(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_subscription(
            admin.DeleteSubscriptionRequest(), name="name_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = AdminServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.AdminServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [transports.AdminServiceGrpcTransport, transports.AdminServiceGrpcAsyncIOTransport],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = AdminServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client.transport, transports.AdminServiceGrpcTransport,)


def test_admin_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.AdminServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_admin_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.AdminServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_topic",
        "get_topic",
        "get_topic_partitions",
        "list_topics",
        "update_topic",
        "delete_topic",
        "list_topic_subscriptions",
        "create_subscription",
        "get_subscription",
        "list_subscriptions",
        "update_subscription",
        "delete_subscription",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_admin_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.AdminServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_admin_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(auth, "default") as adc, mock.patch(
        "google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.AdminServiceTransport()
        adc.assert_called_once()


def test_admin_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        AdminServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


def test_admin_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.AdminServiceGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_admin_service_host_no_port():
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="pubsublite.googleapis.com"
        ),
    )
    assert client.transport._host == "pubsublite.googleapis.com:443"


def test_admin_service_host_with_port():
    client = AdminServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="pubsublite.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "pubsublite.googleapis.com:8000"


def test_admin_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.AdminServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_admin_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.AdminServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


@pytest.mark.parametrize(
    "transport_class",
    [transports.AdminServiceGrpcTransport, transports.AdminServiceGrpcAsyncIOTransport],
)
def test_admin_service_transport_channel_mtls_with_client_cert_source(transport_class):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


@pytest.mark.parametrize(
    "transport_class",
    [transports.AdminServiceGrpcTransport, transports.AdminServiceGrpcAsyncIOTransport],
)
def test_admin_service_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_subscription_path():
    project = "squid"
    location = "clam"
    subscription = "whelk"

    expected = "projects/{project}/locations/{location}/subscriptions/{subscription}".format(
        project=project, location=location, subscription=subscription,
    )
    actual = AdminServiceClient.subscription_path(project, location, subscription)
    assert expected == actual


def test_parse_subscription_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "subscription": "nudibranch",
    }
    path = AdminServiceClient.subscription_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_subscription_path(path)
    assert expected == actual


def test_topic_path():
    project = "cuttlefish"
    location = "mussel"
    topic = "winkle"

    expected = "projects/{project}/locations/{location}/topics/{topic}".format(
        project=project, location=location, topic=topic,
    )
    actual = AdminServiceClient.topic_path(project, location, topic)
    assert expected == actual


def test_parse_topic_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "topic": "abalone",
    }
    path = AdminServiceClient.topic_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_topic_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "squid"

    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = AdminServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = AdminServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "whelk"

    expected = "folders/{folder}".format(folder=folder,)
    actual = AdminServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = AdminServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "oyster"

    expected = "organizations/{organization}".format(organization=organization,)
    actual = AdminServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = AdminServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "cuttlefish"

    expected = "projects/{project}".format(project=project,)
    actual = AdminServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = AdminServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "winkle"
    location = "nautilus"

    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = AdminServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = AdminServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.AdminServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = AdminServiceClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.AdminServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = AdminServiceClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
