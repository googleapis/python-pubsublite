from typing import Optional

from google.api_core.client_options import ClientOptions

from google.cloud.pubsublite.admin_client import AdminClient
from google.cloud.pubsublite.endpoints import regional_endpoint
from google.cloud.pubsublite.internal.wire.admin_client_impl import AdminClientImpl
from google.cloud.pubsublite.location import CloudRegion
from google.cloud.pubsublite_v1 import AdminServiceClient
from google.auth.credentials import Credentials


def make_admin_client(
    region: CloudRegion,
    credentials: Optional[Credentials] = None,
    client_options: Optional[ClientOptions] = None,
) -> AdminClient:
    if client_options is None:
        client_options = ClientOptions(api_endpoint=regional_endpoint(region))
    return AdminClientImpl(
        AdminServiceClient(client_options=client_options, credentials=credentials),
        region,
    )
