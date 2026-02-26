"""Zephyr Squad Cloud API client."""

import logging
from typing import Any

import requests

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.squad.config import ZephyrSquadConfig
from zephyr_mcp.squad.jwt_auth import generate_jwt_token

logger = logging.getLogger("mcp-zephyr-squad")

API_PREFIX = "/public/rest/api/1.0"


class ZephyrSquadClient:
    """Base client for Zephyr Squad Cloud API interactions."""

    def __init__(self, config: ZephyrSquadConfig) -> None:
        self.config = config
        self.base_url = (config.base_url or "").rstrip("/")
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"

    def _get_auth_headers(self, method: str, relative_path: str, query_params: dict[str, str] | None = None) -> dict[str, str]:
        """Generate JWT auth headers for a specific request."""
        token = generate_jwt_token(
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
            account_id=self.config.account_id,
            http_method=method,
            relative_path=relative_path,
            query_params=query_params,
        )
        return {
            "Authorization": f"JWT {token}",
            "zapiAccessKey": self.config.access_key,
        }

    def request(self, method: str, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an HTTP request to the Zephyr Squad Cloud API."""
        relative_path = f"{API_PREFIX}{endpoint}"
        url = f"{self.base_url}{relative_path}"
        logger.debug(f"Zephyr Squad API request: {method.upper()} {url}")

        auth_headers = self._get_auth_headers(method, relative_path, query_params)
        headers = {**auth_headers, **kwargs.pop("headers", {})}

        if query_params:
            kwargs["params"] = query_params

        response = self.session.request(method, url, headers=headers, **kwargs)

        if response.status_code in (401, 403):
            raise ZephyrAuthenticationError(f"Authentication failed for Zephyr Squad API: {response.status_code} {response.text}")

        response.raise_for_status()

        if response.status_code == 204:
            return {}

        return response.json()

    def get(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a GET request."""
        return self.request("GET", endpoint, query_params=query_params, **kwargs)

    def post(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a POST request."""
        return self.request("POST", endpoint, query_params=query_params, **kwargs)

    def put(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a PUT request."""
        return self.request("PUT", endpoint, query_params=query_params, **kwargs)

    def delete(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, query_params=query_params, **kwargs)
