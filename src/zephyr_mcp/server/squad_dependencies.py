"""Dependency providers for SquadFetcher with context awareness."""

from __future__ import annotations

import logging

from fastmcp import Context

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.squad import SquadFetcher, ZephyrSquadConfig

logger = logging.getLogger("mcp-zephyr-squad.server.dependencies")


async def get_squad_fetcher(ctx: Context) -> SquadFetcher:
    """Returns a SquadFetcher instance appropriate for the current request context."""
    logger.debug("get_squad_fetcher: ENTERED.")

    # Try global config from lifespan context
    app_ctx = _get_app_context(ctx)
    if app_ctx and app_ctx.squad_config:
        logger.debug("get_squad_fetcher: Using squad config from lifespan context.")
        return SquadFetcher(config=app_ctx.squad_config)

    # Try loading from environment as fallback
    try:
        config = ZephyrSquadConfig.from_env()
        return SquadFetcher(config=config)
    except ValueError:
        pass

    logger.error("Zephyr Squad configuration could not be resolved.")
    raise ValueError(
        "Zephyr Squad client not available. Configure either: "
        "PAT mode (ZEPHYR_SQUAD_PAT_TOKEN + ZEPHYR_SQUAD_JIRA_BASE_URL) or "
        "JWT mode (ZEPHYR_SQUAD_ACCESS_KEY + ZEPHYR_SQUAD_SECRET_KEY + ZEPHYR_SQUAD_ACCOUNT_ID)."
    )


def _get_app_context(ctx: Context) -> AppContext | None:
    """Extract AppContext from the FastMCP lifespan context."""
    lifespan_ctx_dict = ctx.request_context.lifespan_context
    if isinstance(lifespan_ctx_dict, dict):
        return lifespan_ctx_dict.get("app_lifespan_context")
    return None
