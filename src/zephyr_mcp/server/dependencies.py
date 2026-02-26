"""Dependency providers for ZephyrFetcher with context awareness."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import Context

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.zephyr import ZephyrConfig, ZephyrFetcher

logger = logging.getLogger("mcp-zephyr.server.dependencies")


async def get_zephyr_fetcher(ctx: Context) -> ZephyrFetcher:
    """Returns a ZephyrFetcher instance appropriate for the current request context."""
    logger.debug(f"get_zephyr_fetcher: ENTERED. Context ID: {id(ctx)}")

    # Try HTTP request context first (for SSE transport with per-request auth)
    try:
        from fastmcp.server.dependencies import get_http_request
        from starlette.requests import Request

        request: Request = get_http_request()
        logger.debug(f"get_zephyr_fetcher: In HTTP request context. Request URL: {request.url}")

        if hasattr(request.state, "zephyr_fetcher") and request.state.zephyr_fetcher:
            logger.debug("get_zephyr_fetcher: Returning ZephyrFetcher from request.state.")
            return request.state.zephyr_fetcher

        user_auth_type = getattr(request.state, "user_auth_type", None)
        logger.debug(f"get_zephyr_fetcher: User auth type: {user_auth_type}")

        service_headers = getattr(request.state, "service_headers", {})
        zephyr_url_header = service_headers.get("X-Zephyr-Url")
        zephyr_token_header = service_headers.get("X-Zephyr-Personal-Token")

        if user_auth_type == "pat" and zephyr_url_header and zephyr_token_header and not hasattr(request.state, "user_token"):
            logger.info(f"Creating header-based ZephyrFetcher with URL: {zephyr_url_header}")
            header_config = ZephyrConfig(
                url=zephyr_url_header,
                auth_type="pat",
                personal_token=zephyr_token_header,
                ssl_verify=True,
            )
            try:
                header_zephyr_fetcher = ZephyrFetcher(config=header_config)
                request.state.zephyr_fetcher = header_zephyr_fetcher
                return header_zephyr_fetcher
            except Exception as e:
                logger.error(f"get_zephyr_fetcher: Failed to create header-based ZephyrFetcher: {e}", exc_info=True)
                raise ValueError(f"Invalid header-based Zephyr token or configuration: {e}") from e

        elif user_auth_type in ["oauth", "pat"] and hasattr(request.state, "user_token"):
            user_token = getattr(request.state, "user_token", None)
            if not user_token:
                raise ValueError("User token found in state but is empty.")

            app_lifespan_ctx = _get_app_context(ctx)
            if not app_lifespan_ctx or not app_lifespan_ctx.full_zephyr_config:
                raise ValueError("Zephyr global configuration is not available from lifespan context.")

            user_specific_config = _create_user_config(
                base_config=app_lifespan_ctx.full_zephyr_config,
                auth_type=user_auth_type,
                token=user_token,
            )
            try:
                user_zephyr_fetcher = ZephyrFetcher(config=user_specific_config)
                request.state.zephyr_fetcher = user_zephyr_fetcher
                return user_zephyr_fetcher
            except Exception as e:
                logger.error(f"get_zephyr_fetcher: Failed to create user-specific ZephyrFetcher: {e}")
                raise ValueError(f"Invalid user Zephyr token or configuration: {e}") from e
        else:
            logger.debug(f"get_zephyr_fetcher: No user-specific auth. Auth type: {user_auth_type}. Will use global fallback.")

    except RuntimeError:
        logger.debug("Not in an HTTP request context. Attempting global ZephyrFetcher.")

    # Fall back to global config from lifespan context
    app_lifespan_ctx = _get_app_context(ctx)
    if app_lifespan_ctx and app_lifespan_ctx.full_zephyr_config:
        logger.debug(f"get_zephyr_fetcher: Using global config. auth_type: {app_lifespan_ctx.full_zephyr_config.auth_type}")
        return ZephyrFetcher(config=app_lifespan_ctx.full_zephyr_config)

    logger.error("Zephyr configuration could not be resolved.")
    raise ValueError("Zephyr client (fetcher) not available. Ensure server is configured correctly.")


def _get_app_context(ctx: Context) -> AppContext | None:
    """Extract AppContext from the FastMCP lifespan context."""
    lifespan_ctx_dict = ctx.request_context.lifespan_context
    if isinstance(lifespan_ctx_dict, dict):
        return lifespan_ctx_dict.get("app_lifespan_context")
    return None


def _create_user_config(base_config: ZephyrConfig, auth_type: str, token: str) -> ZephyrConfig:
    """Create a user-specific ZephyrConfig from a base config and per-request credentials."""
    import dataclasses

    changes: dict[str, Any] = {"auth_type": auth_type}

    if auth_type == "oauth":
        from zephyr_mcp.utils.oauth import BYOAccessTokenOAuthConfig

        changes["oauth_config"] = BYOAccessTokenOAuthConfig(access_token=token)
        changes["personal_token"] = None
        changes["email"] = None
        changes["api_token"] = None
    elif auth_type == "pat":
        changes["personal_token"] = token
        changes["oauth_config"] = None
        changes["email"] = None
        changes["api_token"] = None
    else:
        raise ValueError(f"Unsupported auth_type for user config: {auth_type}")

    return dataclasses.replace(base_config, **changes)
