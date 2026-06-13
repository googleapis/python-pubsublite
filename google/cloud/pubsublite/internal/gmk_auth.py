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

import base64
import json
import time
import urllib.request
from typing import Tuple

import google.auth
import google.auth.transport.requests

# Static JWT header matching Java/Go implementations
GMK_JWT_HEADER = {"typ": "JWT", "alg": "GOOG_OAUTH2_TOKEN"}


def _b64_encode(data: str) -> str:
    # base64url encoding without padding
    return base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8").rstrip("=")


def _extract_email(credentials) -> str:
    # Attempt to extract email from credentials
    if (
        hasattr(credentials, "service_account_email")
        and credentials.service_account_email
    ):
        return credentials.service_account_email
    if hasattr(credentials, "signer_email") and credentials.signer_email:
        return credentials.signer_email

    # Fallback to userinfo endpoint if we have a token
    if hasattr(credentials, "token") and credentials.token:
        try:
            req = urllib.request.Request(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {credentials.token}"},
            )
            # Use a short timeout to avoid blocking indefinitely
            with urllib.request.urlopen(req, timeout=5) as response:
                info = json.loads(response.read().decode("utf-8"))
                return info.get("email", "")
        except Exception:
            pass
    return ""


def gcp_oauth_callback(oauth_config: str) -> Tuple[str, float]:
    """Callback for confluent-kafka OAUTHBEARER authentication.

    Args:
        oauth_config: Custom configuration string from sasl.oauthbearer.config (ignored).

    Returns:
        A tuple of (token_value_str, expiry_time_seconds_since_epoch).
    """
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)

    email = _extract_email(credentials)
    now = int(time.time())
    # Default to 1 hour if expiry is not available
    expiry = int(credentials.expiry.timestamp()) if credentials.expiry else now + 3600

    claims = {
        "exp": expiry,
        "iat": now,
        "scope": "kafka",
        "sub": email,
    }

    # Token format: base64url(header).base64url(claims).base64url(access_token)
    # Ensure separators are compact (no spaces) to match Go/Java JSON encoding exactly
    header_json = json.dumps(GMK_JWT_HEADER, separators=(",", ":"))
    claims_json = json.dumps(claims, separators=(",", ":"))

    header_b64 = _b64_encode(header_json)
    claims_b64 = _b64_encode(claims_json)
    token_b64 = (
        base64.urlsafe_b64encode(credentials.token.encode("utf-8"))
        .decode("utf-8")
        .rstrip("=")
    )

    kafka_token = f"{header_b64}.{claims_b64}.{token_b64}"
    return kafka_token, float(expiry)
