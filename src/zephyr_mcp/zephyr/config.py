"""Configuration for the Zephyr Scale API client."""

import logging
import os
from dataclasses import dataclass

from zephyr_mcp.utils.env import get_custom_headers, is_env_ssl_verify
from zephyr_mcp.utils.oauth import OAuthConfig, get_oauth_config_from_env
from zephyr_mcp.utils.urls import is_atlassian_cloud_url

logger = logging.getLogger("mcp-zephyr")


@dataclass
class ZephyrConfig:
    """Configuration for the Zephyr Scale API client."""

    url: str | None = None
    auth_type: str = "pat"
    personal_token: str | None = None
    email: str | None = None
    api_token: str | None = None
    oauth_config: OAuthConfig | None = None
    ssl_verify: bool = True
    project_key: str | None = None
    http_proxy: str | None = None
    https_proxy: str | None = None
    no_proxy: str | None = None
    socks_proxy: str | None = None
    custom_headers: dict[str, str] | None = None

    @property
    def is_cloud(self) -> bool:
        """Check if the Zephyr URL is an Atlassian Cloud URL."""
        return is_atlassian_cloud_url(self.url)

    @classmethod
    def from_env(cls) -> "ZephyrConfig":
        """Create configuration from environment variables."""
        url = os.getenv("ZEPHYR_URL")
        personal_token = os.getenv("ZEPHYR_PERSONAL_TOKEN")
        email = os.getenv("ZEPHYR_EMAIL")
        api_token = os.getenv("ZEPHYR_API_TOKEN")
        project_key = os.getenv("ZEPHYR_PROJECT_KEY")

        http_proxy = os.getenv("ZEPHYR_HTTP_PROXY") or os.getenv("HTTP_PROXY")
        https_proxy = os.getenv("ZEPHYR_HTTPS_PROXY") or os.getenv("HTTPS_PROXY")
        no_proxy = os.getenv("ZEPHYR_NO_PROXY") or os.getenv("NO_PROXY")
        socks_proxy = os.getenv("ZEPHYR_SOCKS_PROXY") or os.getenv("SOCKS_PROXY")

        ssl_verify = is_env_ssl_verify("ZEPHYR_SSL_VERIFY")
        custom_headers = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")

        oauth_config = None
        auth_type = "pat"

        if personal_token:
            auth_type = "pat"
        elif email and api_token:
            auth_type = "basic"
        else:
            oauth_result = get_oauth_config_from_env(service_url=url)
            if oauth_result is not None:
                if isinstance(oauth_result, OAuthConfig):
                    oauth_config = oauth_result
                    auth_type = "oauth"
                else:
                    auth_type = "bearer"
                    personal_token = oauth_result.access_token

        if not url:
            raise ValueError("ZEPHYR_URL environment variable is required but not set. Please set it to your Zephyr Scale API URL.")

        if auth_type == "pat" and not personal_token:
            if not (email and api_token):
                raise ValueError(
                    "Zephyr Scale authentication is not configured. Please set either:\n"
                    "  - ZEPHYR_PERSONAL_TOKEN for Personal Access Token authentication, or\n"
                    "  - ZEPHYR_EMAIL and ZEPHYR_API_TOKEN for basic authentication, or\n"
                    "  - OAuth environment variables for OAuth authentication."
                )

        logger.info(f"Zephyr Scale configuration loaded: auth_type={auth_type}, url={url}")

        return cls(
            url=url,
            auth_type=auth_type,
            personal_token=personal_token,
            email=email,
            api_token=api_token,
            oauth_config=oauth_config,
            ssl_verify=ssl_verify,
            project_key=project_key,
            http_proxy=http_proxy,
            https_proxy=https_proxy,
            no_proxy=no_proxy,
            socks_proxy=socks_proxy,
            custom_headers=custom_headers or None,
        )
