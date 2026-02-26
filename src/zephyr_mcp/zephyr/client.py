"""Zephyr Scale API client."""

import base64
import logging
from typing import Any

import requests

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.utils.logging import get_masked_session_headers, mask_sensitive
from zephyr_mcp.utils.oauth import configure_oauth_session
from zephyr_mcp.utils.ssl import configure_ssl_verification
from zephyr_mcp.zephyr.config import ZephyrConfig

logger = logging.getLogger("mcp-zephyr")


class ZephyrClient:
    """Base client for Zephyr Scale API interactions."""

    def __init__(self, config: ZephyrConfig) -> None:
        self.config = config
        self.base_url = (config.url or "").rstrip("/")
        self.session = requests.Session()

        self._configure_proxies()
        self._configure_auth()

        configure_ssl_verification(
            service_name="Zephyr",
            url=self.base_url,
            session=self.session,
            ssl_verify=config.ssl_verify,
        )

        if config.custom_headers:
            self.session.headers.update(config.custom_headers)

        logger.debug(f"Session headers (masked): {get_masked_session_headers(dict(self.session.headers))}")

    def _configure_proxies(self) -> None:
        """Configure proxy settings for the session."""
        proxies: dict[str, str] = {}
        if self.config.socks_proxy:
            proxies["http"] = self.config.socks_proxy
            proxies["https"] = self.config.socks_proxy
        else:
            if self.config.http_proxy:
                proxies["http"] = self.config.http_proxy
            if self.config.https_proxy:
                proxies["https"] = self.config.https_proxy

        if proxies:
            self.session.proxies.update(proxies)

        if self.config.no_proxy:
            import os

            os.environ["NO_PROXY"] = self.config.no_proxy

    def _configure_auth(self) -> None:
        """Configure authentication for the session."""
        auth_type = self.config.auth_type
        logger.info(f"Configuring Zephyr auth: type={auth_type}")

        if auth_type == "oauth" and self.config.oauth_config:
            if not configure_oauth_session(self.session, self.config.oauth_config):
                raise ZephyrAuthenticationError("Failed to configure OAuth session for Zephyr")
            logger.info("OAuth authentication configured for Zephyr")

        elif auth_type in ("bearer", "pat") and self.config.personal_token:
            self.session.headers["Authorization"] = f"Bearer {self.config.personal_token}"
            logger.info(f"Bearer/PAT authentication configured: token={mask_sensitive(self.config.personal_token)}")

        elif auth_type == "basic" and self.config.email and self.config.api_token:
            credentials = base64.b64encode(f"{self.config.email}:{self.config.api_token}".encode()).decode()
            self.session.headers["Authorization"] = f"Basic {credentials}"
            logger.info(f"Basic authentication configured for Zephyr: email={self.config.email}")

        else:
            raise ZephyrAuthenticationError(f"Unable to configure Zephyr authentication with auth_type='{auth_type}'")

    def request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an HTTP request to the Zephyr Scale API."""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Zephyr API request: {method.upper()} {url}")

        response = self.session.request(method, url, **kwargs)

        if response.status_code in (401, 403):
            raise ZephyrAuthenticationError(f"Authentication failed for Zephyr API: {response.status_code} {response.text}")

        response.raise_for_status()

        if response.status_code == 204:
            return {}

        return response.json()

    def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)
