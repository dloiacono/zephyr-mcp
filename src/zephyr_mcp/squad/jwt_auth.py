"""JWT authentication for Zephyr Squad Cloud API."""

import hashlib
import logging
import time
from urllib.parse import urlencode

import jwt

logger = logging.getLogger("mcp-zephyr-squad")

JWT_EXPIRY_SECONDS = 3600


def generate_jwt_token(
    access_key: str,
    secret_key: str,
    account_id: str,
    http_method: str,
    relative_path: str,
    query_params: dict[str, str] | None = None,
) -> str:
    """Generate a JWT token for a Zephyr Squad Cloud API request.

    Each API call requires a unique JWT token based on the HTTP method,
    relative path, and query parameters.
    """
    canonical_path = _build_canonical_path(http_method, relative_path, query_params)
    qsh = hashlib.sha256(canonical_path.encode("utf-8")).hexdigest()

    now = int(time.time())
    payload = {
        "sub": account_id,
        "qsh": qsh,
        "iss": access_key,
        "iat": now,
        "exp": now + JWT_EXPIRY_SECONDS,
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    logger.debug(f"Generated JWT for {http_method} {relative_path}")
    return token


def _build_canonical_path(
    http_method: str,
    relative_path: str,
    query_params: dict[str, str] | None = None,
) -> str:
    """Build the canonical path string for QSH generation.

    Format: METHOD&relative_path&sorted_query_string
    """
    method = http_method.upper()
    query_string = ""
    if query_params:
        sorted_params = sorted(query_params.items())
        query_string = urlencode(sorted_params)
    return f"{method}&{relative_path}&{query_string}"
