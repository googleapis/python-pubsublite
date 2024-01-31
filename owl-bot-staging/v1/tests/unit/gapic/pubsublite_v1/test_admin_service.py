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
import os
# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
    from unittest.mock import AsyncMock  # pragma: NO COVER
except ImportError:  # pragma: NO COVER
    import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from google.api_core import api_core_version
from proto.marshal.rules.dates import DurationRule, TimestampRule
from proto.marshal.rules import wrappers

from google.api_core import client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.api_core import path_template
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.pubsublite_v1.services.admin_service import AdminServiceAsyncClient
from google.cloud.pubsublite_v1.services.admin_service import AdminServiceClient
from google.cloud.pubsublite_v1.services.admin_service import pagers
from google.cloud.pubsublite_v1.services.admin_service import transports
from google.cloud.pubsublite_v1.types import admin
from google.cloud.pubsublite_v1.types import common
from google.longrunning import operations_pb2 # type: ignore
from google.oauth2 import service_account
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
import google.auth


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"

# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return "foo.googleapis.com" if ("localhost" in client.DEFAULT_ENDPOINT) else client.DEFAULT_ENDPOINT

# If default endpoint template is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint template so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint_template(client):
    return "test.{UNIVERSE_DOMAIN}" if ("localhost" in client._DEFAULT_ENDPOINT_TEMPLATE) else client._DEFAULT_ENDPOINT_TEMPLATE

# Anonymous Credentials with universe domain property. If no universe domain is provided, then
# the default universe domain is "googleapis.com".
class _AnonymousCredentialsWithUniverseDomain(ga_credentials.AnonymousCredentials):
    def __init__(self, universe_domain="googleapis.com"):
        super(_AnonymousCredentialsWithUniverseDomain, self).__init__()
        self._universe_domain = universe_domain

    @property
    def universe_domain(self):
        return self._universe_domain

def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert AdminServiceClient._get_default_mtls_endpoint(None) is None
    assert AdminServiceClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert AdminServiceClient._get_default_mtls_endpoint(api_mtls_endpoint) == api_mtls_endpoint
    assert AdminServiceClient._get_default_mtls_endpoint(sandbox_endpoint) == sandbox_mtls_endpoint
    assert AdminServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint) == sandbox_mtls_endpoint
    assert AdminServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi

def test__read_environment_variables():
    assert AdminServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        assert AdminServiceClient._read_environment_variables() == (True, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        assert AdminServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}):
        with pytest.raises(ValueError) as excinfo:
            AdminServiceClient._read_environment_variables()
    assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        assert AdminServiceClient._read_environment_variables() == (False, "never", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        assert AdminServiceClient._read_environment_variables() == (False, "always", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"}):
        assert AdminServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            AdminServiceClient._read_environment_variables()
    assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"

    with mock.patch.dict(os.environ, {"GOOGLE_CLOUD_UNIVERSE_DOMAIN": "foo.com"}):
        assert AdminServiceClient._read_environment_variables() == (False, "auto", "foo.com")

def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert AdminServiceClient._get_client_cert_source(None, False) is None
    assert AdminServiceClient._get_client_cert_source(mock_provided_cert_source, False) is None
    assert AdminServiceClient._get_client_cert_source(mock_provided_cert_source, True) == mock_provided_cert_source

    with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
        with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=mock_default_cert_source):
            assert AdminServiceClient._get_client_cert_source(None, True) is mock_default_cert_source
            assert AdminServiceClient._get_client_cert_source(mock_provided_cert_source, "true") is mock_provided_cert_source

@mock.patch.object(AdminServiceClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceClient))
@mock.patch.object(AdminServiceAsyncClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceAsyncClient))
def test__get_api_endpoint():
    api_override = "foo.com"
    mock_client_cert_source = mock.Mock()
    default_universe = AdminServiceClient._DEFAULT_UNIVERSE
    default_endpoint = AdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=default_universe)
    mock_universe = "bar.com"
    mock_endpoint = AdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=mock_universe)

    assert AdminServiceClient._get_api_endpoint(api_override, mock_client_cert_source, default_universe, "always") == api_override
    assert AdminServiceClient._get_api_endpoint(None, mock_client_cert_source, default_universe, "auto") == AdminServiceClient.DEFAULT_MTLS_ENDPOINT
    assert AdminServiceClient._get_api_endpoint(None, None, default_universe, "auto") == default_endpoint
    assert AdminServiceClient._get_api_endpoint(None, None, default_universe, "always") == AdminServiceClient.DEFAULT_MTLS_ENDPOINT
    assert AdminServiceClient._get_api_endpoint(None, mock_client_cert_source, default_universe, "always") == AdminServiceClient.DEFAULT_MTLS_ENDPOINT
    assert AdminServiceClient._get_api_endpoint(None, None, mock_universe, "never") == mock_endpoint
    assert AdminServiceClient._get_api_endpoint(None, None, default_universe, "never") == default_endpoint

    with pytest.raises(MutualTLSChannelError) as excinfo:
        AdminServiceClient._get_api_endpoint(None, mock_client_cert_source, mock_universe, "auto")
    assert str(excinfo.value) == "mTLS is not supported in any universe other than googleapis.com."

def test__get_universe_domain():
    client_universe_domain = "foo.com"
    universe_domain_env = "bar.com"

    assert AdminServiceClient._get_universe_domain(client_universe_domain, universe_domain_env) == client_universe_domain
    assert AdminServiceClient._get_universe_domain(None, universe_domain_env) == universe_domain_env
    assert AdminServiceClient._get_universe_domain(None, None) == AdminServiceClient._DEFAULT_UNIVERSE

    with pytest.raises(ValueError) as excinfo:
        AdminServiceClient._get_universe_domain("", None)
    assert str(excinfo.value) == "Universe Domain cannot be an empty string."

@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc"),
])
def test__validate_universe_domain(client_class, transport_class, transport_name):
    client = client_class(
        transport=transport_class(
            credentials=_AnonymousCredentialsWithUniverseDomain()
        )
    )
    assert client._validate_universe_domain() == True

    # Test the case when universe is already validated.
    assert client._validate_universe_domain() == True

    if transport_name == "grpc":
        # Test the case where credentials are provided by the
        # `local_channel_credentials`. The default universes in both match.
        channel = grpc.secure_channel('http://localhost/', grpc.local_channel_credentials())
        client = client_class(transport=transport_class(channel=channel))
        assert client._validate_universe_domain() == True

        # Test the case where credentials do not exist: e.g. a transport is provided
        # with no credentials. Validation should still succeed because there is no
        # mismatch with non-existent credentials.
        channel = grpc.secure_channel('http://localhost/', grpc.local_channel_credentials())
        transport=transport_class(channel=channel)
        transport._credentials = None
        client = client_class(transport=transport)
        assert client._validate_universe_domain() == True

    # Test the case when there is a universe mismatch from the credentials.
    client = client_class(
        transport=transport_class(credentials=_AnonymousCredentialsWithUniverseDomain(universe_domain="foo.com"))
    )
    with pytest.raises(ValueError) as excinfo:
        client._validate_universe_domain()
    assert str(excinfo.value) == "The configured universe domain (googleapis.com) does not match the universe domain found in the credentials (foo.com). If you haven't configured the universe domain explicitly, `googleapis.com` is the default."

    # Test the case when there is a universe mismatch from the client.
    #
    # TODO: Make this test unconditional once the minimum supported version of
    # google-api-core becomes 2.15.0 or higher.
    api_core_major, api_core_minor, _ = [int(part) for part in api_core_version.__version__.split(".")]
    if api_core_major > 2 or (api_core_major == 2 and api_core_minor >= 15):
        client = client_class(client_options={"universe_domain": "bar.com"}, transport=transport_class(credentials=_AnonymousCredentialsWithUniverseDomain(),))
        with pytest.raises(ValueError) as excinfo:
            client._validate_universe_domain()
        assert str(excinfo.value) == "The configured universe domain (bar.com) does not match the universe domain found in the credentials (googleapis.com). If you haven't configured the universe domain explicitly, `googleapis.com` is the default."

@pytest.mark.parametrize("client_class,transport_name", [
    (AdminServiceClient, "grpc"),
    (AdminServiceAsyncClient, "grpc_asyncio"),
])
def test_admin_service_client_from_service_account_info(client_class, transport_name):
    creds = _AnonymousCredentialsWithUniverseDomain()
    with mock.patch.object(service_account.Credentials, 'from_service_account_info') as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info, transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            'pubsublite.googleapis.com:443'
        )


@pytest.mark.parametrize("transport_class,transport_name", [
    (transports.AdminServiceGrpcTransport, "grpc"),
    (transports.AdminServiceGrpcAsyncIOTransport, "grpc_asyncio"),
])
def test_admin_service_client_service_account_always_use_jwt(transport_class, transport_name):
    with mock.patch.object(service_account.Credentials, 'with_always_use_jwt_access', create=True) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=True)
        use_jwt.assert_called_once_with(True)

    with mock.patch.object(service_account.Credentials, 'with_always_use_jwt_access', create=True) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=False)
        use_jwt.assert_not_called()


@pytest.mark.parametrize("client_class,transport_name", [
    (AdminServiceClient, "grpc"),
    (AdminServiceAsyncClient, "grpc_asyncio"),
])
def test_admin_service_client_from_service_account_file(client_class, transport_name):
    creds = _AnonymousCredentialsWithUniverseDomain()
    with mock.patch.object(service_account.Credentials, 'from_service_account_file') as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json", transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json("dummy/file/path.json", transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            'pubsublite.googleapis.com:443'
        )


def test_admin_service_client_get_transport_class():
    transport = AdminServiceClient.get_transport_class()
    available_transports = [
        transports.AdminServiceGrpcTransport,
    ]
    assert transport in available_transports

    transport = AdminServiceClient.get_transport_class("grpc")
    assert transport == transports.AdminServiceGrpcTransport


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc"),
    (AdminServiceAsyncClient, transports.AdminServiceGrpcAsyncIOTransport, "grpc_asyncio"),
])
@mock.patch.object(AdminServiceClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceClient))
@mock.patch.object(AdminServiceAsyncClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceAsyncClient))
def test_admin_service_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(AdminServiceClient, 'get_transport_class') as gtc:
        transport = transport_class(
            credentials=_AnonymousCredentialsWithUniverseDomain()
        )
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(AdminServiceClient, 'get_transport_class') as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(transport=transport_name, client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            client = client_class(transport=transport_name)
    assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}):
        with pytest.raises(ValueError) as excinfo:
            client = client_class(transport=transport_name)
    assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )
    # Check the case api_endpoint is provided
    options = client_options.ClientOptions(api_audience="https://language.googleapis.com")
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience="https://language.googleapis.com"
        )

@pytest.mark.parametrize("client_class,transport_class,transport_name,use_client_cert_env", [
    (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc", "true"),
    (AdminServiceAsyncClient, transports.AdminServiceGrpcAsyncIOTransport, "grpc_asyncio", "true"),
    (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc", "false"),
    (AdminServiceAsyncClient, transports.AdminServiceGrpcAsyncIOTransport, "grpc_asyncio", "false"),
])
@mock.patch.object(AdminServiceClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceClient))
@mock.patch.object(AdminServiceAsyncClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceAsyncClient))
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_admin_service_client_mtls_env_auto(client_class, transport_class, transport_name, use_client_cert_env):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        options = client_options.ClientOptions(client_cert_source=client_cert_source_callback)
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class(client_options=options, transport=transport_name)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE)
            else:
                expected_client_cert_source = client_cert_source_callback
                expected_host = client.DEFAULT_MTLS_ENDPOINT

            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=expected_host,
                scopes=None,
                client_cert_source_for_mtls=expected_client_cert_source,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
                with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=client_cert_source_callback):
                    if use_client_cert_env == "false":
                        expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE)
                        expected_client_cert_source = None
                    else:
                        expected_host = client.DEFAULT_MTLS_ENDPOINT
                        expected_client_cert_source = client_cert_source_callback

                    patched.return_value = None
                    client = client_class(transport=transport_name)
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                        always_use_jwt_access=True,
                        api_audience=None,
                    )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch("google.auth.transport.mtls.has_default_client_cert_source", return_value=False):
                patched.return_value = None
                client = client_class(transport=transport_name)
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                    always_use_jwt_access=True,
                    api_audience=None,
                )


@pytest.mark.parametrize("client_class", [
    AdminServiceClient, AdminServiceAsyncClient
])
@mock.patch.object(AdminServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AdminServiceClient))
@mock.patch.object(AdminServiceAsyncClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AdminServiceAsyncClient))
def test_admin_service_client_get_mtls_endpoint_and_cert_source(client_class):
    mock_client_cert_source = mock.Mock()

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "true".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint)
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(options)
        assert api_endpoint == mock_api_endpoint
        assert cert_source == mock_client_cert_source

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "false".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        mock_client_cert_source = mock.Mock()
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint)
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(options)
        assert api_endpoint == mock_api_endpoint
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert doesn't exist.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=False):
            api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
            assert api_endpoint == client_class.DEFAULT_ENDPOINT
            assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert exists.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
            with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=mock_client_cert_source):
                api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
                assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
                assert cert_source == mock_client_cert_source

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            client_class.get_mtls_endpoint_and_cert_source()

        assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}):
        with pytest.raises(ValueError) as excinfo:
            client_class.get_mtls_endpoint_and_cert_source()

        assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"

@pytest.mark.parametrize("client_class", [
    AdminServiceClient, AdminServiceAsyncClient
])
@mock.patch.object(AdminServiceClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceClient))
@mock.patch.object(AdminServiceAsyncClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AdminServiceAsyncClient))
def test_admin_service_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = AdminServiceClient._DEFAULT_UNIVERSE
    default_endpoint = AdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=default_universe)
    mock_universe = "bar.com"
    mock_endpoint = AdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=mock_universe)

    # If ClientOptions.api_endpoint is set and GOOGLE_API_USE_CLIENT_CERTIFICATE="true",
    # use ClientOptions.api_endpoint as the api endpoint regardless.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch("google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"):
            options = client_options.ClientOptions(client_cert_source=mock_client_cert_source, api_endpoint=api_override)
            client = client_class(client_options=options, credentials=_AnonymousCredentialsWithUniverseDomain())
            assert client.api_endpoint == api_override

    # If ClientOptions.api_endpoint is not set and GOOGLE_API_USE_MTLS_ENDPOINT="never",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with GDU as the api endpoint.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        client = client_class(credentials=_AnonymousCredentialsWithUniverseDomain())
        assert client.api_endpoint == default_endpoint

    # If ClientOptions.api_endpoint is not set and GOOGLE_API_USE_MTLS_ENDPOINT="always",
    # use the DEFAULT_MTLS_ENDPOINT as the api endpoint.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        client = client_class(credentials=_AnonymousCredentialsWithUniverseDomain())
        assert client.api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT

    # If ClientOptions.api_endpoint is not set, GOOGLE_API_USE_MTLS_ENDPOINT="auto" (default),
    # GOOGLE_API_USE_CLIENT_CERTIFICATE="false" (default), default cert source doesn't exist,
    # and ClientOptions.universe_domain="bar.com",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with universe domain as the api endpoint.
    options = client_options.ClientOptions()
    universe_exists = hasattr(options, "universe_domain")
    if universe_exists:
        options = client_options.ClientOptions(universe_domain=mock_universe)
        client = client_class(client_options=options, credentials=_AnonymousCredentialsWithUniverseDomain())
    else:
        client = client_class(client_options=options, credentials=_AnonymousCredentialsWithUniverseDomain())
    assert client.api_endpoint == (mock_endpoint if universe_exists else default_endpoint)
    assert client.universe_domain == (mock_universe if universe_exists else default_universe)

    # If ClientOptions does not have a universe domain attribute and GOOGLE_API_USE_MTLS_ENDPOINT="never",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with GDU as the api endpoint.
    options = client_options.ClientOptions()
    if hasattr(options, "universe_domain"):
        delattr(options, "universe_domain")
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        client = client_class(client_options=options, credentials=_AnonymousCredentialsWithUniverseDomain())
        assert client.api_endpoint == default_endpoint


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc"),
    (AdminServiceAsyncClient, transports.AdminServiceGrpcAsyncIOTransport, "grpc_asyncio"),
])
def test_admin_service_client_client_options_scopes(client_class, transport_class, transport_name):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(
        scopes=["1", "2"],
    )
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

@pytest.mark.parametrize("client_class,transport_class,transport_name,grpc_helpers", [
    (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc", grpc_helpers),
    (AdminServiceAsyncClient, transports.AdminServiceGrpcAsyncIOTransport, "grpc_asyncio", grpc_helpers_async),
])
def test_admin_service_client_client_options_credentials_file(client_class, transport_class, transport_name, grpc_helpers):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(
        credentials_file="credentials.json"
    )

    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

def test_admin_service_client_client_options_from_dict():
    with mock.patch('google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceGrpcTransport.__init__') as grpc_transport:
        grpc_transport.return_value = None
        client = AdminServiceClient(
            client_options={'api_endpoint': 'squid.clam.whelk'}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize("client_class,transport_class,transport_name,grpc_helpers", [
    (AdminServiceClient, transports.AdminServiceGrpcTransport, "grpc", grpc_helpers),
    (AdminServiceAsyncClient, transports.AdminServiceGrpcAsyncIOTransport, "grpc_asyncio", grpc_helpers_async),
])
def test_admin_service_client_create_channel_credentials_file(client_class, transport_class, transport_name, grpc_helpers):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(
        credentials_file="credentials.json"
    )

    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # test that the credentials from file are saved and used as the credentials.
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel"
    ) as create_channel:
        creds = _AnonymousCredentialsWithUniverseDomain()
        file_creds = _AnonymousCredentialsWithUniverseDomain()
        load_creds.return_value = (file_creds, None)
        adc.return_value = (creds, None)
        client = client_class(client_options=options, transport=transport_name)
        create_channel.assert_called_with(
            "pubsublite.googleapis.com:443",
            credentials=file_creds,
            credentials_file=None,
            quota_project_id=None,
            default_scopes=(
                'https://www.googleapis.com/auth/cloud-platform',
),
            scopes=None,
            default_host="pubsublite.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize("request_type", [
  admin.CreateTopicRequest,
  dict,
])
def test_create_topic(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic(
            name='name_value',
        )
        response = client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)
    assert response.name == 'name_value'


def test_create_topic_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_topic),
            '__call__') as call:
        client.create_topic()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateTopicRequest()

@pytest.mark.asyncio
async def test_create_topic_async(transport: str = 'grpc_asyncio', request_type=admin.CreateTopicRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Topic(
            name='name_value',
        ))
        response = await client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)
    assert response.name == 'name_value'


@pytest.mark.asyncio
async def test_create_topic_async_from_dict():
    await test_create_topic_async(request_type=dict)


def test_create_topic_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateTopicRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_topic),
            '__call__') as call:
        call.return_value = common.Topic()
        client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_create_topic_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateTopicRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_topic),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        await client.create_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_create_topic_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_topic(
            parent='parent_value',
            topic=common.Topic(name='name_value'),
            topic_id='topic_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].topic
        mock_val = common.Topic(name='name_value')
        assert arg == mock_val
        arg = args[0].topic_id
        mock_val = 'topic_id_value'
        assert arg == mock_val


def test_create_topic_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_topic(
            admin.CreateTopicRequest(),
            parent='parent_value',
            topic=common.Topic(name='name_value'),
            topic_id='topic_id_value',
        )

@pytest.mark.asyncio
async def test_create_topic_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_topic(
            parent='parent_value',
            topic=common.Topic(name='name_value'),
            topic_id='topic_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].topic
        mock_val = common.Topic(name='name_value')
        assert arg == mock_val
        arg = args[0].topic_id
        mock_val = 'topic_id_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_create_topic_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_topic(
            admin.CreateTopicRequest(),
            parent='parent_value',
            topic=common.Topic(name='name_value'),
            topic_id='topic_id_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.GetTopicRequest,
  dict,
])
def test_get_topic(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic(
            name='name_value',
        )
        response = client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)
    assert response.name == 'name_value'


def test_get_topic_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic),
            '__call__') as call:
        client.get_topic()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetTopicRequest()

@pytest.mark.asyncio
async def test_get_topic_async(transport: str = 'grpc_asyncio', request_type=admin.GetTopicRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Topic(
            name='name_value',
        ))
        response = await client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)
    assert response.name == 'name_value'


@pytest.mark.asyncio
async def test_get_topic_async_from_dict():
    await test_get_topic_async(request_type=dict)


def test_get_topic_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic),
            '__call__') as call:
        call.return_value = common.Topic()
        client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_topic_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        await client.get_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_topic_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_topic(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_topic_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_topic(
            admin.GetTopicRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_topic_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_topic(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_topic_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_topic(
            admin.GetTopicRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.GetTopicPartitionsRequest,
  dict,
])
def test_get_topic_partitions(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic_partitions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.TopicPartitions(
            partition_count=1634,
        )
        response = client.get_topic_partitions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetTopicPartitionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, admin.TopicPartitions)
    assert response.partition_count == 1634


def test_get_topic_partitions_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic_partitions),
            '__call__') as call:
        client.get_topic_partitions()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetTopicPartitionsRequest()

@pytest.mark.asyncio
async def test_get_topic_partitions_async(transport: str = 'grpc_asyncio', request_type=admin.GetTopicPartitionsRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic_partitions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(admin.TopicPartitions(
            partition_count=1634,
        ))
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
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicPartitionsRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic_partitions),
            '__call__') as call:
        call.return_value = admin.TopicPartitions()
        client.get_topic_partitions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_topic_partitions_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetTopicPartitionsRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic_partitions),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.TopicPartitions())
        await client.get_topic_partitions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_topic_partitions_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic_partitions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.TopicPartitions()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_topic_partitions(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_topic_partitions_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_topic_partitions(
            admin.GetTopicPartitionsRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_topic_partitions_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_topic_partitions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.TopicPartitions()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.TopicPartitions())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_topic_partitions(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_topic_partitions_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_topic_partitions(
            admin.GetTopicPartitionsRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.ListTopicsRequest,
  dict,
])
def test_list_topics(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicsResponse(
            next_page_token='next_page_token_value',
        )
        response = client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListTopicsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTopicsPager)
    assert response.next_page_token == 'next_page_token_value'


def test_list_topics_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        client.list_topics()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListTopicsRequest()

@pytest.mark.asyncio
async def test_list_topics_async(transport: str = 'grpc_asyncio', request_type=admin.ListTopicsRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(admin.ListTopicsResponse(
            next_page_token='next_page_token_value',
        ))
        response = await client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListTopicsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTopicsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
async def test_list_topics_async_from_dict():
    await test_list_topics_async(request_type=dict)


def test_list_topics_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        call.return_value = admin.ListTopicsResponse()
        client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_topics_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListTopicsResponse())
        await client.list_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_list_topics_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_topics(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_list_topics_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_topics(
            admin.ListTopicsRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_list_topics_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListTopicsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_topics(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_topics_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_topics(
            admin.ListTopicsRequest(),
            parent='parent_value',
        )


def test_list_topics_pager(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                    common.Topic(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_topics(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, common.Topic)
                   for i in results)
def test_list_topics_pages(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                    common.Topic(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_topics(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_topics_async_pager():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                    common.Topic(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_topics(request={},)
        assert async_pager.next_page_token == 'abc'
        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, common.Topic)
                for i in responses)


@pytest.mark.asyncio
async def test_list_topics_async_pages():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topics),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                    common.Topic(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicsResponse(
                topics=[
                    common.Topic(),
                    common.Topic(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in ( # pragma: no branch
            await client.list_topics(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  admin.UpdateTopicRequest,
  dict,
])
def test_update_topic(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic(
            name='name_value',
        )
        response = client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)
    assert response.name == 'name_value'


def test_update_topic_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_topic),
            '__call__') as call:
        client.update_topic()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateTopicRequest()

@pytest.mark.asyncio
async def test_update_topic_async(transport: str = 'grpc_asyncio', request_type=admin.UpdateTopicRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Topic(
            name='name_value',
        ))
        response = await client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateTopicRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Topic)
    assert response.name == 'name_value'


@pytest.mark.asyncio
async def test_update_topic_async_from_dict():
    await test_update_topic_async(request_type=dict)


def test_update_topic_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateTopicRequest()

    request.topic.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_topic),
            '__call__') as call:
        call.return_value = common.Topic()
        client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'topic.name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_update_topic_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateTopicRequest()

    request.topic.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_topic),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        await client.update_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'topic.name=name_value',
    ) in kw['metadata']


def test_update_topic_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_topic(
            topic=common.Topic(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].topic
        mock_val = common.Topic(name='name_value')
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=['paths_value'])
        assert arg == mock_val


def test_update_topic_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_topic(
            admin.UpdateTopicRequest(),
            topic=common.Topic(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

@pytest.mark.asyncio
async def test_update_topic_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Topic()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Topic())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_topic(
            topic=common.Topic(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].topic
        mock_val = common.Topic(name='name_value')
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=['paths_value'])
        assert arg == mock_val

@pytest.mark.asyncio
async def test_update_topic_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_topic(
            admin.UpdateTopicRequest(),
            topic=common.Topic(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )


@pytest.mark.parametrize("request_type", [
  admin.DeleteTopicRequest,
  dict,
])
def test_delete_topic(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.DeleteTopicRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_topic_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_topic),
            '__call__') as call:
        client.delete_topic()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.DeleteTopicRequest()

@pytest.mark.asyncio
async def test_delete_topic_async(transport: str = 'grpc_asyncio', request_type=admin.DeleteTopicRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_topic),
            '__call__') as call:
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
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteTopicRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_topic),
            '__call__') as call:
        call.return_value = None
        client.delete_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_delete_topic_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteTopicRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_topic),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.delete_topic(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_delete_topic_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_topic(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_delete_topic_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_topic(
            admin.DeleteTopicRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_delete_topic_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_topic),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_topic(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_delete_topic_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_topic(
            admin.DeleteTopicRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.ListTopicSubscriptionsRequest,
  dict,
])
def test_list_topic_subscriptions(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicSubscriptionsResponse(
            subscriptions=['subscriptions_value'],
            next_page_token='next_page_token_value',
        )
        response = client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListTopicSubscriptionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTopicSubscriptionsPager)
    assert response.subscriptions == ['subscriptions_value']
    assert response.next_page_token == 'next_page_token_value'


def test_list_topic_subscriptions_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        client.list_topic_subscriptions()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListTopicSubscriptionsRequest()

@pytest.mark.asyncio
async def test_list_topic_subscriptions_async(transport: str = 'grpc_asyncio', request_type=admin.ListTopicSubscriptionsRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(admin.ListTopicSubscriptionsResponse(
            subscriptions=['subscriptions_value'],
            next_page_token='next_page_token_value',
        ))
        response = await client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListTopicSubscriptionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTopicSubscriptionsAsyncPager)
    assert response.subscriptions == ['subscriptions_value']
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
async def test_list_topic_subscriptions_async_from_dict():
    await test_list_topic_subscriptions_async(request_type=dict)


def test_list_topic_subscriptions_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicSubscriptionsRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        call.return_value = admin.ListTopicSubscriptionsResponse()
        client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_topic_subscriptions_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListTopicSubscriptionsRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListTopicSubscriptionsResponse())
        await client.list_topic_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_list_topic_subscriptions_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicSubscriptionsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_topic_subscriptions(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_list_topic_subscriptions_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_topic_subscriptions(
            admin.ListTopicSubscriptionsRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_list_topic_subscriptions_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListTopicSubscriptionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListTopicSubscriptionsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_topic_subscriptions(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_topic_subscriptions_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_topic_subscriptions(
            admin.ListTopicSubscriptionsRequest(),
            name='name_value',
        )


def test_list_topic_subscriptions_pager(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('name', ''),
            )),
        )
        pager = client.list_topic_subscriptions(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, str)
                   for i in results)
def test_list_topic_subscriptions_pages(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_topic_subscriptions(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_topic_subscriptions_async_pager():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_topic_subscriptions(request={},)
        assert async_pager.next_page_token == 'abc'
        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, str)
                for i in responses)


@pytest.mark.asyncio
async def test_list_topic_subscriptions_async_pages():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_topic_subscriptions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListTopicSubscriptionsResponse(
                subscriptions=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in ( # pragma: no branch
            await client.list_topic_subscriptions(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  admin.CreateSubscriptionRequest,
  dict,
])
def test_create_subscription(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription(
            name='name_value',
            topic='topic_value',
        )
        response = client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)
    assert response.name == 'name_value'
    assert response.topic == 'topic_value'


def test_create_subscription_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_subscription),
            '__call__') as call:
        client.create_subscription()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateSubscriptionRequest()

@pytest.mark.asyncio
async def test_create_subscription_async(transport: str = 'grpc_asyncio', request_type=admin.CreateSubscriptionRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription(
            name='name_value',
            topic='topic_value',
        ))
        response = await client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)
    assert response.name == 'name_value'
    assert response.topic == 'topic_value'


@pytest.mark.asyncio
async def test_create_subscription_async_from_dict():
    await test_create_subscription_async(request_type=dict)


def test_create_subscription_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateSubscriptionRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_subscription),
            '__call__') as call:
        call.return_value = common.Subscription()
        client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_create_subscription_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateSubscriptionRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_subscription),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        await client.create_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_create_subscription_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_subscription(
            parent='parent_value',
            subscription=common.Subscription(name='name_value'),
            subscription_id='subscription_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].subscription
        mock_val = common.Subscription(name='name_value')
        assert arg == mock_val
        arg = args[0].subscription_id
        mock_val = 'subscription_id_value'
        assert arg == mock_val


def test_create_subscription_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_subscription(
            admin.CreateSubscriptionRequest(),
            parent='parent_value',
            subscription=common.Subscription(name='name_value'),
            subscription_id='subscription_id_value',
        )

@pytest.mark.asyncio
async def test_create_subscription_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_subscription(
            parent='parent_value',
            subscription=common.Subscription(name='name_value'),
            subscription_id='subscription_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].subscription
        mock_val = common.Subscription(name='name_value')
        assert arg == mock_val
        arg = args[0].subscription_id
        mock_val = 'subscription_id_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_create_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_subscription(
            admin.CreateSubscriptionRequest(),
            parent='parent_value',
            subscription=common.Subscription(name='name_value'),
            subscription_id='subscription_id_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.GetSubscriptionRequest,
  dict,
])
def test_get_subscription(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription(
            name='name_value',
            topic='topic_value',
        )
        response = client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)
    assert response.name == 'name_value'
    assert response.topic == 'topic_value'


def test_get_subscription_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_subscription),
            '__call__') as call:
        client.get_subscription()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetSubscriptionRequest()

@pytest.mark.asyncio
async def test_get_subscription_async(transport: str = 'grpc_asyncio', request_type=admin.GetSubscriptionRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription(
            name='name_value',
            topic='topic_value',
        ))
        response = await client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)
    assert response.name == 'name_value'
    assert response.topic == 'topic_value'


@pytest.mark.asyncio
async def test_get_subscription_async_from_dict():
    await test_get_subscription_async(request_type=dict)


def test_get_subscription_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetSubscriptionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_subscription),
            '__call__') as call:
        call.return_value = common.Subscription()
        client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_subscription_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetSubscriptionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_subscription),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        await client.get_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_subscription_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_subscription(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_subscription_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_subscription(
            admin.GetSubscriptionRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_subscription_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_subscription(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_subscription(
            admin.GetSubscriptionRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.ListSubscriptionsRequest,
  dict,
])
def test_list_subscriptions(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListSubscriptionsResponse(
            next_page_token='next_page_token_value',
        )
        response = client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListSubscriptionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSubscriptionsPager)
    assert response.next_page_token == 'next_page_token_value'


def test_list_subscriptions_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        client.list_subscriptions()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListSubscriptionsRequest()

@pytest.mark.asyncio
async def test_list_subscriptions_async(transport: str = 'grpc_asyncio', request_type=admin.ListSubscriptionsRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(admin.ListSubscriptionsResponse(
            next_page_token='next_page_token_value',
        ))
        response = await client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListSubscriptionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSubscriptionsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
async def test_list_subscriptions_async_from_dict():
    await test_list_subscriptions_async(request_type=dict)


def test_list_subscriptions_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListSubscriptionsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        call.return_value = admin.ListSubscriptionsResponse()
        client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_subscriptions_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListSubscriptionsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListSubscriptionsResponse())
        await client.list_subscriptions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_list_subscriptions_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListSubscriptionsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_subscriptions(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_list_subscriptions_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_subscriptions(
            admin.ListSubscriptionsRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_list_subscriptions_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListSubscriptionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListSubscriptionsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_subscriptions(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_subscriptions_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_subscriptions(
            admin.ListSubscriptionsRequest(),
            parent='parent_value',
        )


def test_list_subscriptions_pager(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token='abc',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                ],
                next_page_token='ghi',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_subscriptions(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, common.Subscription)
                   for i in results)
def test_list_subscriptions_pages(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token='abc',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                ],
                next_page_token='ghi',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_subscriptions(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_subscriptions_async_pager():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token='abc',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                ],
                next_page_token='ghi',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_subscriptions(request={},)
        assert async_pager.next_page_token == 'abc'
        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, common.Subscription)
                for i in responses)


@pytest.mark.asyncio
async def test_list_subscriptions_async_pages():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_subscriptions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                    common.Subscription(),
                ],
                next_page_token='abc',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[],
                next_page_token='def',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                ],
                next_page_token='ghi',
            ),
            admin.ListSubscriptionsResponse(
                subscriptions=[
                    common.Subscription(),
                    common.Subscription(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in ( # pragma: no branch
            await client.list_subscriptions(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  admin.UpdateSubscriptionRequest,
  dict,
])
def test_update_subscription(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription(
            name='name_value',
            topic='topic_value',
        )
        response = client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)
    assert response.name == 'name_value'
    assert response.topic == 'topic_value'


def test_update_subscription_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_subscription),
            '__call__') as call:
        client.update_subscription()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateSubscriptionRequest()

@pytest.mark.asyncio
async def test_update_subscription_async(transport: str = 'grpc_asyncio', request_type=admin.UpdateSubscriptionRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription(
            name='name_value',
            topic='topic_value',
        ))
        response = await client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Subscription)
    assert response.name == 'name_value'
    assert response.topic == 'topic_value'


@pytest.mark.asyncio
async def test_update_subscription_async_from_dict():
    await test_update_subscription_async(request_type=dict)


def test_update_subscription_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateSubscriptionRequest()

    request.subscription.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_subscription),
            '__call__') as call:
        call.return_value = common.Subscription()
        client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'subscription.name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_update_subscription_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateSubscriptionRequest()

    request.subscription.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_subscription),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        await client.update_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'subscription.name=name_value',
    ) in kw['metadata']


def test_update_subscription_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_subscription(
            subscription=common.Subscription(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].subscription
        mock_val = common.Subscription(name='name_value')
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=['paths_value'])
        assert arg == mock_val


def test_update_subscription_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_subscription(
            admin.UpdateSubscriptionRequest(),
            subscription=common.Subscription(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

@pytest.mark.asyncio
async def test_update_subscription_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Subscription()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Subscription())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_subscription(
            subscription=common.Subscription(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].subscription
        mock_val = common.Subscription(name='name_value')
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=['paths_value'])
        assert arg == mock_val

@pytest.mark.asyncio
async def test_update_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_subscription(
            admin.UpdateSubscriptionRequest(),
            subscription=common.Subscription(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )


@pytest.mark.parametrize("request_type", [
  admin.DeleteSubscriptionRequest,
  dict,
])
def test_delete_subscription(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.DeleteSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_subscription_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_subscription),
            '__call__') as call:
        client.delete_subscription()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.DeleteSubscriptionRequest()

@pytest.mark.asyncio
async def test_delete_subscription_async(transport: str = 'grpc_asyncio', request_type=admin.DeleteSubscriptionRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_subscription),
            '__call__') as call:
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
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteSubscriptionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_subscription),
            '__call__') as call:
        call.return_value = None
        client.delete_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_delete_subscription_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteSubscriptionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_subscription),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.delete_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_delete_subscription_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_subscription(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_delete_subscription_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_subscription(
            admin.DeleteSubscriptionRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_delete_subscription_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_subscription(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_delete_subscription_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_subscription(
            admin.DeleteSubscriptionRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.SeekSubscriptionRequest,
  dict,
])
def test_seek_subscription(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.seek_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')
        response = client.seek_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.SeekSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_seek_subscription_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.seek_subscription),
            '__call__') as call:
        client.seek_subscription()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.SeekSubscriptionRequest()

@pytest.mark.asyncio
async def test_seek_subscription_async(transport: str = 'grpc_asyncio', request_type=admin.SeekSubscriptionRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.seek_subscription),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        response = await client.seek_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.SeekSubscriptionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_seek_subscription_async_from_dict():
    await test_seek_subscription_async(request_type=dict)


def test_seek_subscription_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.SeekSubscriptionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.seek_subscription),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.seek_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_seek_subscription_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.SeekSubscriptionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.seek_subscription),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(operations_pb2.Operation(name='operations/op'))
        await client.seek_subscription(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.parametrize("request_type", [
  admin.CreateReservationRequest,
  dict,
])
def test_create_reservation(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation(
            name='name_value',
            throughput_capacity=2055,
        )
        response = client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Reservation)
    assert response.name == 'name_value'
    assert response.throughput_capacity == 2055


def test_create_reservation_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_reservation),
            '__call__') as call:
        client.create_reservation()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateReservationRequest()

@pytest.mark.asyncio
async def test_create_reservation_async(transport: str = 'grpc_asyncio', request_type=admin.CreateReservationRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation(
            name='name_value',
            throughput_capacity=2055,
        ))
        response = await client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.CreateReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Reservation)
    assert response.name == 'name_value'
    assert response.throughput_capacity == 2055


@pytest.mark.asyncio
async def test_create_reservation_async_from_dict():
    await test_create_reservation_async(request_type=dict)


def test_create_reservation_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateReservationRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_reservation),
            '__call__') as call:
        call.return_value = common.Reservation()
        client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_create_reservation_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.CreateReservationRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_reservation),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation())
        await client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_create_reservation_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_reservation(
            parent='parent_value',
            reservation=common.Reservation(name='name_value'),
            reservation_id='reservation_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].reservation
        mock_val = common.Reservation(name='name_value')
        assert arg == mock_val
        arg = args[0].reservation_id
        mock_val = 'reservation_id_value'
        assert arg == mock_val


def test_create_reservation_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_reservation(
            admin.CreateReservationRequest(),
            parent='parent_value',
            reservation=common.Reservation(name='name_value'),
            reservation_id='reservation_id_value',
        )

@pytest.mark.asyncio
async def test_create_reservation_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_reservation(
            parent='parent_value',
            reservation=common.Reservation(name='name_value'),
            reservation_id='reservation_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].reservation
        mock_val = common.Reservation(name='name_value')
        assert arg == mock_val
        arg = args[0].reservation_id
        mock_val = 'reservation_id_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_create_reservation_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_reservation(
            admin.CreateReservationRequest(),
            parent='parent_value',
            reservation=common.Reservation(name='name_value'),
            reservation_id='reservation_id_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.GetReservationRequest,
  dict,
])
def test_get_reservation(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation(
            name='name_value',
            throughput_capacity=2055,
        )
        response = client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Reservation)
    assert response.name == 'name_value'
    assert response.throughput_capacity == 2055


def test_get_reservation_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_reservation),
            '__call__') as call:
        client.get_reservation()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetReservationRequest()

@pytest.mark.asyncio
async def test_get_reservation_async(transport: str = 'grpc_asyncio', request_type=admin.GetReservationRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation(
            name='name_value',
            throughput_capacity=2055,
        ))
        response = await client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.GetReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Reservation)
    assert response.name == 'name_value'
    assert response.throughput_capacity == 2055


@pytest.mark.asyncio
async def test_get_reservation_async_from_dict():
    await test_get_reservation_async(request_type=dict)


def test_get_reservation_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetReservationRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_reservation),
            '__call__') as call:
        call.return_value = common.Reservation()
        client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_reservation_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.GetReservationRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_reservation),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation())
        await client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_reservation_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_reservation(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_reservation_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_reservation(
            admin.GetReservationRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_reservation_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_reservation(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_reservation_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_reservation(
            admin.GetReservationRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.ListReservationsRequest,
  dict,
])
def test_list_reservations(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListReservationsResponse(
            next_page_token='next_page_token_value',
        )
        response = client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListReservationsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReservationsPager)
    assert response.next_page_token == 'next_page_token_value'


def test_list_reservations_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        client.list_reservations()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListReservationsRequest()

@pytest.mark.asyncio
async def test_list_reservations_async(transport: str = 'grpc_asyncio', request_type=admin.ListReservationsRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(admin.ListReservationsResponse(
            next_page_token='next_page_token_value',
        ))
        response = await client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListReservationsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReservationsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
async def test_list_reservations_async_from_dict():
    await test_list_reservations_async(request_type=dict)


def test_list_reservations_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListReservationsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        call.return_value = admin.ListReservationsResponse()
        client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_reservations_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListReservationsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListReservationsResponse())
        await client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_list_reservations_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListReservationsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_reservations(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_list_reservations_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_reservations(
            admin.ListReservationsRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_list_reservations_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListReservationsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListReservationsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_reservations(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_reservations_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_reservations(
            admin.ListReservationsRequest(),
            parent='parent_value',
        )


def test_list_reservations_pager(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                    common.Reservation(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationsResponse(
                reservations=[],
                next_page_token='def',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_reservations(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, common.Reservation)
                   for i in results)
def test_list_reservations_pages(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                    common.Reservation(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationsResponse(
                reservations=[],
                next_page_token='def',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_reservations(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_reservations_async_pager():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                    common.Reservation(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationsResponse(
                reservations=[],
                next_page_token='def',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_reservations(request={},)
        assert async_pager.next_page_token == 'abc'
        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, common.Reservation)
                for i in responses)


@pytest.mark.asyncio
async def test_list_reservations_async_pages():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservations),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                    common.Reservation(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationsResponse(
                reservations=[],
                next_page_token='def',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationsResponse(
                reservations=[
                    common.Reservation(),
                    common.Reservation(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in ( # pragma: no branch
            await client.list_reservations(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  admin.UpdateReservationRequest,
  dict,
])
def test_update_reservation(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation(
            name='name_value',
            throughput_capacity=2055,
        )
        response = client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Reservation)
    assert response.name == 'name_value'
    assert response.throughput_capacity == 2055


def test_update_reservation_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_reservation),
            '__call__') as call:
        client.update_reservation()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateReservationRequest()

@pytest.mark.asyncio
async def test_update_reservation_async(transport: str = 'grpc_asyncio', request_type=admin.UpdateReservationRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation(
            name='name_value',
            throughput_capacity=2055,
        ))
        response = await client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.UpdateReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, common.Reservation)
    assert response.name == 'name_value'
    assert response.throughput_capacity == 2055


@pytest.mark.asyncio
async def test_update_reservation_async_from_dict():
    await test_update_reservation_async(request_type=dict)


def test_update_reservation_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateReservationRequest()

    request.reservation.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_reservation),
            '__call__') as call:
        call.return_value = common.Reservation()
        client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'reservation.name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_update_reservation_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.UpdateReservationRequest()

    request.reservation.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_reservation),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation())
        await client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'reservation.name=name_value',
    ) in kw['metadata']


def test_update_reservation_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_reservation(
            reservation=common.Reservation(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].reservation
        mock_val = common.Reservation(name='name_value')
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=['paths_value'])
        assert arg == mock_val


def test_update_reservation_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_reservation(
            admin.UpdateReservationRequest(),
            reservation=common.Reservation(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

@pytest.mark.asyncio
async def test_update_reservation_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.update_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = common.Reservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(common.Reservation())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_reservation(
            reservation=common.Reservation(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].reservation
        mock_val = common.Reservation(name='name_value')
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=['paths_value'])
        assert arg == mock_val

@pytest.mark.asyncio
async def test_update_reservation_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_reservation(
            admin.UpdateReservationRequest(),
            reservation=common.Reservation(name='name_value'),
            update_mask=field_mask_pb2.FieldMask(paths=['paths_value']),
        )


@pytest.mark.parametrize("request_type", [
  admin.DeleteReservationRequest,
  dict,
])
def test_delete_reservation(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.DeleteReservationRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_reservation_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_reservation),
            '__call__') as call:
        client.delete_reservation()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.DeleteReservationRequest()

@pytest.mark.asyncio
async def test_delete_reservation_async(transport: str = 'grpc_asyncio', request_type=admin.DeleteReservationRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.DeleteReservationRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_reservation_async_from_dict():
    await test_delete_reservation_async(request_type=dict)


def test_delete_reservation_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteReservationRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_reservation),
            '__call__') as call:
        call.return_value = None
        client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_delete_reservation_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.DeleteReservationRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_reservation),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_delete_reservation_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_reservation(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_delete_reservation_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_reservation(
            admin.DeleteReservationRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_delete_reservation_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_reservation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_reservation(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_delete_reservation_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_reservation(
            admin.DeleteReservationRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  admin.ListReservationTopicsRequest,
  dict,
])
def test_list_reservation_topics(request_type, transport: str = 'grpc'):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListReservationTopicsResponse(
            topics=['topics_value'],
            next_page_token='next_page_token_value',
        )
        response = client.list_reservation_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListReservationTopicsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReservationTopicsPager)
    assert response.topics == ['topics_value']
    assert response.next_page_token == 'next_page_token_value'


def test_list_reservation_topics_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        client.list_reservation_topics()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListReservationTopicsRequest()

@pytest.mark.asyncio
async def test_list_reservation_topics_async(transport: str = 'grpc_asyncio', request_type=admin.ListReservationTopicsRequest):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(admin.ListReservationTopicsResponse(
            topics=['topics_value'],
            next_page_token='next_page_token_value',
        ))
        response = await client.list_reservation_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == admin.ListReservationTopicsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReservationTopicsAsyncPager)
    assert response.topics == ['topics_value']
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
async def test_list_reservation_topics_async_from_dict():
    await test_list_reservation_topics_async(request_type=dict)


def test_list_reservation_topics_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListReservationTopicsRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        call.return_value = admin.ListReservationTopicsResponse()
        client.list_reservation_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_reservation_topics_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = admin.ListReservationTopicsRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListReservationTopicsResponse())
        await client.list_reservation_topics(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_list_reservation_topics_flattened():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListReservationTopicsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_reservation_topics(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_list_reservation_topics_flattened_error():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_reservation_topics(
            admin.ListReservationTopicsRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_list_reservation_topics_flattened_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = admin.ListReservationTopicsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(admin.ListReservationTopicsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_reservation_topics(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_reservation_topics_flattened_error_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_reservation_topics(
            admin.ListReservationTopicsRequest(),
            name='name_value',
        )


def test_list_reservation_topics_pager(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('name', ''),
            )),
        )
        pager = client.list_reservation_topics(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, str)
                   for i in results)
def test_list_reservation_topics_pages(transport_name: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_reservation_topics(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_reservation_topics_async_pager():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_reservation_topics(request={},)
        assert async_pager.next_page_token == 'abc'
        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, str)
                for i in responses)


@pytest.mark.asyncio
async def test_list_reservation_topics_async_pages():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_reservation_topics),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token='abc',
            ),
            admin.ListReservationTopicsResponse(
                topics=[],
                next_page_token='def',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                ],
                next_page_token='ghi',
            ),
            admin.ListReservationTopicsResponse(
                topics=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in ( # pragma: no branch
            await client.list_reservation_topics(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            client_options=options,
            credentials=_AnonymousCredentialsWithUniverseDomain()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    with pytest.raises(ValueError):
        client = AdminServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    client = AdminServiceClient(transport=transport)
    assert client.transport is transport

def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AdminServiceGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.AdminServiceGrpcAsyncIOTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    channel = transport.grpc_channel
    assert channel

@pytest.mark.parametrize("transport_class", [
    transports.AdminServiceGrpcTransport,
    transports.AdminServiceGrpcAsyncIOTransport,
])
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, 'default') as adc:
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport_class()
        adc.assert_called_once()

@pytest.mark.parametrize("transport_name", [
    "grpc",
])
def test_transport_kind(transport_name):
    transport = AdminServiceClient.get_transport_class(transport_name)(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    assert transport.kind == transport_name

def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    assert isinstance(
        client.transport,
        transports.AdminServiceGrpcTransport,
    )

def test_admin_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.AdminServiceTransport(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            credentials_file="credentials.json"
        )


def test_admin_service_base_transport():
    # Instantiate the base transport.
    with mock.patch('google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceTransport.__init__') as Transport:
        Transport.return_value = None
        transport = transports.AdminServiceTransport(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        'create_topic',
        'get_topic',
        'get_topic_partitions',
        'list_topics',
        'update_topic',
        'delete_topic',
        'list_topic_subscriptions',
        'create_subscription',
        'get_subscription',
        'list_subscriptions',
        'update_subscription',
        'delete_subscription',
        'seek_subscription',
        'create_reservation',
        'get_reservation',
        'list_reservations',
        'update_reservation',
        'delete_reservation',
        'list_reservation_topics',
        'get_operation',
        'cancel_operation',
        'delete_operation',
        'list_operations',
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    with pytest.raises(NotImplementedError):
        transport.close()

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client

    # Catch all for all remaining methods and properties
    remainder = [
        'kind',
    ]
    for r in remainder:
        with pytest.raises(NotImplementedError):
            getattr(transport, r)()


def test_admin_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(google.auth, 'load_credentials_from_file', autospec=True) as load_creds, mock.patch('google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        load_creds.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport = transports.AdminServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with("credentials.json",
            scopes=None,
            default_scopes=(
            'https://www.googleapis.com/auth/cloud-platform',
),
            quota_project_id="octopus",
        )


def test_admin_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc, mock.patch('google.cloud.pubsublite_v1.services.admin_service.transports.AdminServiceTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport = transports.AdminServiceTransport()
        adc.assert_called_once()


def test_admin_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc:
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        AdminServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=(
            'https://www.googleapis.com/auth/cloud-platform',
),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.AdminServiceGrpcTransport,
        transports.AdminServiceGrpcAsyncIOTransport,
    ],
)
def test_admin_service_transport_auth_adc(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc:
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])
        adc.assert_called_once_with(
            scopes=["1", "2"],
            default_scopes=(                'https://www.googleapis.com/auth/cloud-platform',),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.AdminServiceGrpcTransport,
        transports.AdminServiceGrpcAsyncIOTransport,
    ],
)
def test_admin_service_transport_auth_gdch_credentials(transport_class):
    host = 'https://language.com'
    api_audience_tests = [None, 'https://language2.com']
    api_audience_expect = [host, 'https://language2.com']
    for t, e in zip(api_audience_tests, api_audience_expect):
        with mock.patch.object(google.auth, 'default', autospec=True) as adc:
            gdch_mock = mock.MagicMock()
            type(gdch_mock).with_gdch_audience = mock.PropertyMock(return_value=gdch_mock)
            adc.return_value = (gdch_mock, None)
            transport_class(host=host, api_audience=t)
            gdch_mock.with_gdch_audience.assert_called_once_with(
                e
            )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.AdminServiceGrpcTransport, grpc_helpers),
        (transports.AdminServiceGrpcAsyncIOTransport, grpc_helpers_async)
    ],
)
def test_admin_service_transport_create_channel(transport_class, grpc_helpers):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = _AnonymousCredentialsWithUniverseDomain()
        adc.return_value = (creds, None)
        transport_class(
            quota_project_id="octopus",
            scopes=["1", "2"]
        )

        create_channel.assert_called_with(
            "pubsublite.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            default_scopes=(
                'https://www.googleapis.com/auth/cloud-platform',
),
            scopes=["1", "2"],
            default_host="pubsublite.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize("transport_class", [transports.AdminServiceGrpcTransport, transports.AdminServiceGrpcAsyncIOTransport])
def test_admin_service_grpc_transport_client_cert_source_for_mtls(
    transport_class
):
    cred = _AnonymousCredentialsWithUniverseDomain()

    # Check ssl_channel_credentials is used if provided.
    with mock.patch.object(transport_class, "create_channel") as mock_create_channel:
        mock_ssl_channel_creds = mock.Mock()
        transport_class(
            host="squid.clam.whelk",
            credentials=cred,
            ssl_channel_credentials=mock_ssl_channel_creds
        )
        mock_create_channel.assert_called_once_with(
            "squid.clam.whelk:443",
            credentials=cred,
            credentials_file=None,
            scopes=None,
            ssl_credentials=mock_ssl_channel_creds,
            quota_project_id=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )

    # Check if ssl_channel_credentials is not provided, then client_cert_source_for_mtls
    # is used.
    with mock.patch.object(transport_class, "create_channel", return_value=mock.Mock()):
        with mock.patch("grpc.ssl_channel_credentials") as mock_ssl_cred:
            transport_class(
                credentials=cred,
                client_cert_source_for_mtls=client_cert_source_callback
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert,
                private_key=expected_key
            )


@pytest.mark.parametrize("transport_name", [
    "grpc",
    "grpc_asyncio",
])
def test_admin_service_host_no_port(transport_name):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        client_options=client_options.ClientOptions(api_endpoint='pubsublite.googleapis.com'),
         transport=transport_name,
    )
    assert client.transport._host == (
        'pubsublite.googleapis.com:443'
    )

@pytest.mark.parametrize("transport_name", [
    "grpc",
    "grpc_asyncio",
])
def test_admin_service_host_with_port(transport_name):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        client_options=client_options.ClientOptions(api_endpoint='pubsublite.googleapis.com:8000'),
        transport=transport_name,
    )
    assert client.transport._host == (
        'pubsublite.googleapis.com:8000'
    )

def test_admin_service_grpc_transport_channel():
    channel = grpc.secure_channel('http://localhost/', grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.AdminServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_admin_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel('http://localhost/', grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.AdminServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize("transport_class", [transports.AdminServiceGrpcTransport, transports.AdminServiceGrpcAsyncIOTransport])
def test_admin_service_transport_channel_mtls_with_client_cert_source(
    transport_class
):
    with mock.patch("grpc.ssl_channel_credentials", autospec=True) as grpc_ssl_channel_cred:
        with mock.patch.object(transport_class, "create_channel") as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = _AnonymousCredentialsWithUniverseDomain()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(google.auth, 'default') as adc:
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
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize("transport_class", [transports.AdminServiceGrpcTransport, transports.AdminServiceGrpcAsyncIOTransport])
def test_admin_service_transport_channel_mtls_with_adc(
    transport_class
):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(transport_class, "create_channel") as grpc_create_channel:
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
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_admin_service_grpc_lro_client():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc',
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_admin_service_grpc_lro_async_client():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport='grpc_asyncio',
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsAsyncClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_reservation_path():
    project = "squid"
    location = "clam"
    reservation = "whelk"
    expected = "projects/{project}/locations/{location}/reservations/{reservation}".format(project=project, location=location, reservation=reservation, )
    actual = AdminServiceClient.reservation_path(project, location, reservation)
    assert expected == actual


def test_parse_reservation_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "reservation": "nudibranch",
    }
    path = AdminServiceClient.reservation_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_reservation_path(path)
    assert expected == actual

def test_subscription_path():
    project = "cuttlefish"
    location = "mussel"
    subscription = "winkle"
    expected = "projects/{project}/locations/{location}/subscriptions/{subscription}".format(project=project, location=location, subscription=subscription, )
    actual = AdminServiceClient.subscription_path(project, location, subscription)
    assert expected == actual


def test_parse_subscription_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "subscription": "abalone",
    }
    path = AdminServiceClient.subscription_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_subscription_path(path)
    assert expected == actual

def test_topic_path():
    project = "squid"
    location = "clam"
    topic = "whelk"
    expected = "projects/{project}/locations/{location}/topics/{topic}".format(project=project, location=location, topic=topic, )
    actual = AdminServiceClient.topic_path(project, location, topic)
    assert expected == actual


def test_parse_topic_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "topic": "nudibranch",
    }
    path = AdminServiceClient.topic_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_topic_path(path)
    assert expected == actual

def test_common_billing_account_path():
    billing_account = "cuttlefish"
    expected = "billingAccounts/{billing_account}".format(billing_account=billing_account, )
    actual = AdminServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "mussel",
    }
    path = AdminServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_billing_account_path(path)
    assert expected == actual

def test_common_folder_path():
    folder = "winkle"
    expected = "folders/{folder}".format(folder=folder, )
    actual = AdminServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nautilus",
    }
    path = AdminServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_folder_path(path)
    assert expected == actual

def test_common_organization_path():
    organization = "scallop"
    expected = "organizations/{organization}".format(organization=organization, )
    actual = AdminServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "abalone",
    }
    path = AdminServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_organization_path(path)
    assert expected == actual

def test_common_project_path():
    project = "squid"
    expected = "projects/{project}".format(project=project, )
    actual = AdminServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "clam",
    }
    path = AdminServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_project_path(path)
    assert expected == actual

def test_common_location_path():
    project = "whelk"
    location = "octopus"
    expected = "projects/{project}/locations/{location}".format(project=project, location=location, )
    actual = AdminServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
    }
    path = AdminServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = AdminServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(transports.AdminServiceTransport, '_prep_wrapped_messages') as prep:
        client = AdminServiceClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(transports.AdminServiceTransport, '_prep_wrapped_messages') as prep:
        transport_class = AdminServiceClient.get_transport_class()
        transport = transport_class(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

@pytest.mark.asyncio
async def test_transport_close_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc_asyncio",
    )
    with mock.patch.object(type(getattr(client.transport, "grpc_channel")), "close") as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_delete_operation(transport: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.DeleteOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None
@pytest.mark.asyncio
async def test_delete_operation_async(transport: str = "grpc_asyncio"):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.DeleteOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None

def test_delete_operation_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value =  None

        client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]
@pytest.mark.asyncio
async def test_delete_operation_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

def test_delete_operation_from_dict():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()
@pytest.mark.asyncio
async def test_delete_operation_from_dict_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.delete_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_cancel_operation(transport: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None
@pytest.mark.asyncio
async def test_cancel_operation_async(transport: str = "grpc_asyncio"):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None

def test_cancel_operation_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value =  None

        client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]
@pytest.mark.asyncio
async def test_cancel_operation_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

def test_cancel_operation_from_dict():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()
@pytest.mark.asyncio
async def test_cancel_operation_from_dict_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_get_operation(transport: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()
        response = client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)
@pytest.mark.asyncio
async def test_get_operation_async(transport: str = "grpc_asyncio"):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)

def test_get_operation_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = operations_pb2.Operation()

        client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]
@pytest.mark.asyncio
async def test_get_operation_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

def test_get_operation_from_dict():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()

        response = client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()
@pytest.mark.asyncio
async def test_get_operation_from_dict_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_list_operations(transport: str = "grpc"):
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()
        response = client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)
@pytest.mark.asyncio
async def test_list_operations_async(transport: str = "grpc_asyncio"):
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)

def test_list_operations_field_headers():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = operations_pb2.ListOperationsResponse()

        client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]
@pytest.mark.asyncio
async def test_list_operations_field_headers_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

def test_list_operations_from_dict():
    client = AdminServiceClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()

        response = client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()
@pytest.mark.asyncio
async def test_list_operations_from_dict_async():
    client = AdminServiceAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_transport_close():
    transports = {
        "grpc": "_grpc_channel",
    }

    for transport, close_name in transports.items():
        client = AdminServiceClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            transport=transport
        )
        with mock.patch.object(type(getattr(client.transport, close_name)), "close") as close:
            with client:
                close.assert_not_called()
            close.assert_called_once()

def test_client_ctx():
    transports = [
        'grpc',
    ]
    for transport in transports:
        client = AdminServiceClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            transport=transport
        )
        # Test client calls underlying transport.
        with mock.patch.object(type(client.transport), "close") as close:
            close.assert_not_called()
            with client:
                pass
            close.assert_called()

@pytest.mark.parametrize("client_class,transport_class", [
    (AdminServiceClient, transports.AdminServiceGrpcTransport),
    (AdminServiceAsyncClient, transports.AdminServiceGrpcAsyncIOTransport),
])
def test_api_key_credentials(client_class, transport_class):
    with mock.patch.object(
        google.auth._default, "get_api_key_credentials", create=True
    ) as get_api_key_credentials:
        mock_cred = mock.Mock()
        get_api_key_credentials.return_value = mock_cred
        options = client_options.ClientOptions()
        options.api_key = "api_key"
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=mock_cred,
                credentials_file=None,
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )