"""Factory for creating the Zephyr Scale and Squad MCP server."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.squad_tools import (
    squad_add_test_to_cycle,
    squad_create_cycle,
    squad_get_cycle,
    squad_get_cycles,
    squad_get_execution,
    squad_get_executions_by_cycle,
    squad_update_execution,
    squad_zql_search,
)
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
from zephyr_mcp.squad.config import ZephyrSquadConfig
from zephyr_mcp.zephyr.config import ZephyrConfig

logger = logging.getLogger("mcp-zephyr")


def create_server(read_only: bool = False) -> FastMCP:
    """Create and configure the Zephyr MCP server with Scale and Squad support."""

    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
        """Initialize application context on server startup."""
        logger.info("Zephyr MCP server starting up...")

        zephyr_config = None
        try:
            zephyr_config = ZephyrConfig.from_env()
            logger.info(f"Zephyr Scale configuration loaded: auth_type={zephyr_config.auth_type}, url={zephyr_config.url}")
        except Exception as e:
            logger.warning(f"Failed to load Zephyr Scale configuration from environment: {e}")
            logger.warning("Zephyr Scale tools will require per-request authentication via headers.")

        squad_config = None
        try:
            squad_config = ZephyrSquadConfig.from_env()
            logger.info(f"Zephyr Squad configuration loaded: base_url={squad_config.base_url}")
        except Exception as e:
            logger.info(f"Zephyr Squad configuration not available: {e}")

        app_context = AppContext(
            full_zephyr_config=zephyr_config,
            squad_config=squad_config,
            read_only=read_only,
        )

        yield {"app_lifespan_context": app_context}
        logger.info("Zephyr MCP server shutting down.")

    mcp = FastMCP(
        "Zephyr Scale MCP",
        instructions=(
            "MCP server for Zephyr Scale and Zephyr Squad test management - "
            "providing AI-powered access to test cases, test cycles, and test executions."
        ),
        lifespan=lifespan,
    )

    # Register Zephyr Scale read tools
    mcp.tool()(zephyr_get_test_case)
    mcp.tool()(zephyr_search_test_cases)
    mcp.tool()(zephyr_get_test_cycle)
    mcp.tool()(zephyr_get_test_execution)

    # Register Zephyr Scale write tools
    mcp.tool()(zephyr_create_test_case)
    mcp.tool()(zephyr_update_test_case)
    mcp.tool()(zephyr_create_test_cycle)
    mcp.tool()(zephyr_create_test_execution)
    mcp.tool()(zephyr_update_test_execution)
    mcp.tool()(zephyr_link_test_case_to_issue)

    # Register Zephyr Squad read tools
    mcp.tool()(squad_get_cycle)
    mcp.tool()(squad_get_cycles)
    mcp.tool()(squad_get_execution)
    mcp.tool()(squad_get_executions_by_cycle)
    mcp.tool()(squad_zql_search)

    # Register Zephyr Squad write tools
    mcp.tool()(squad_create_cycle)
    mcp.tool()(squad_add_test_to_cycle)
    mcp.tool()(squad_update_execution)

    tool_count = 18
    logger.info(f"Zephyr MCP server created with {tool_count} tools (read_only={read_only})")
    return mcp
