"""Zephyr Squad PAT (Personal Access Token) API client.

Uses Jira's ZAPI endpoints (/rest/zapi/latest/) with PAT or Basic Auth
for Zephyr Squad Server/Data Center and Cloud instances.
"""

import logging
from typing import Any

import requests

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.squad.config import ZephyrSquadConfig

logger = logging.getLogger("mcp-zephyr-squad")

ZAPI_PREFIX = "/rest/zapi/latest"


class ZephyrSquadPatClient:
    """Client for Zephyr Squad via Jira ZAPI endpoints using PAT authentication."""

    def __init__(self, config: ZephyrSquadConfig) -> None:
        self.config = config
        self.base_url = (config.jira_base_url or "").rstrip("/")
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
        self._setup_auth()

    def _setup_auth(self) -> None:
        """Configure session authentication."""
        if self.config.jira_email and self.config.pat_token:
            # Cloud: Basic auth with email + API token
            self.session.auth = (self.config.jira_email, self.config.pat_token)
        elif self.config.pat_token:
            # Server/DC: Bearer token
            self.session.headers["Authorization"] = f"Bearer {self.config.pat_token}"

    def request(self, method: str, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an HTTP request to the Zephyr Squad ZAPI endpoint."""
        url = f"{self.base_url}{ZAPI_PREFIX}{endpoint}"
        logger.debug(f"Zephyr Squad PAT API request: {method.upper()} {url}")

        headers = kwargs.pop("headers", {})

        if query_params:
            kwargs["params"] = query_params

        response = self.session.request(method, url, headers=headers, **kwargs)

        if response.status_code in (401, 403):
            raise ZephyrAuthenticationError(f"Authentication failed for Zephyr Squad ZAPI: {response.status_code} {response.text}")

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
