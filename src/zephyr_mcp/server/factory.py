"""Factory for creating the Zephyr Scale MCP server."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.tools import (
    zephyr_create_test_case,
    zephyr_create_test_cycle,
    zephyr_create_test_execution,
    zephyr_get_test_case,
    zephyr_get_test_cycle,
    zephyr_get_test_execution,
    zephyr_link_test_case_to_issue,
    zephyr_search_test_cases,
    zephyr_update_test_case,
    zephyr_update_test_execution,
)
from zephyr_mcp.zephyr.config import ZephyrConfig

logger = logging.getLogger("mcp-zephyr")


def create_server(read_only: bool = False) -> FastMCP:
    """Create and configure the Zephyr Scale MCP server."""

    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
        """Initialize application context on server startup."""
        logger.info("Zephyr MCP server starting up...")

        zephyr_config = None
        try:
            zephyr_config = ZephyrConfig.from_env()
            logger.info(f"Zephyr configuration loaded: auth_type={zephyr_config.auth_type}, url={zephyr_config.url}")
        except Exception as e:
            logger.warning(f"Failed to load Zephyr configuration from environment: {e}")
            logger.warning("Zephyr tools will require per-request authentication via headers.")

        app_context = AppContext(
            full_zephyr_config=zephyr_config,
            read_only=read_only,
        )

        yield {"app_lifespan_context": app_context}
        logger.info("Zephyr MCP server shutting down.")

    mcp = FastMCP(
        "Zephyr Scale MCP",
        instructions="MCP server for Zephyr Scale test management - providing AI-powered access to test cases, test cycles, and test executions.",
        lifespan=lifespan,
    )

    # Register read tools
    mcp.tool()(zephyr_get_test_case)
    mcp.tool()(zephyr_search_test_cases)
    mcp.tool()(zephyr_get_test_cycle)
    mcp.tool()(zephyr_get_test_execution)

    # Register write tools
    mcp.tool()(zephyr_create_test_case)
    mcp.tool()(zephyr_update_test_case)
    mcp.tool()(zephyr_create_test_cycle)
    mcp.tool()(zephyr_create_test_execution)
    mcp.tool()(zephyr_update_test_execution)
    mcp.tool()(zephyr_link_test_case_to_issue)

    logger.info(f"Zephyr MCP server created with {10} tools (read_only={read_only})")
    return mcp
