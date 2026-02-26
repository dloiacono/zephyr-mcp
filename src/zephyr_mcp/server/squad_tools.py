"""FastMCP tool definitions for the Zephyr Squad MCP server."""

import logging
from typing import Any

from fastmcp import Context

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.server.squad_dependencies import get_squad_fetcher
from zephyr_mcp.squad.executions import SQUAD_EXECUTION_STATUSES
from zephyr_mcp.utils.decorators import check_write_access

logger = logging.getLogger("mcp-zephyr-squad")


async def squad_get_cycle(ctx: Context, cycle_id: str, project_id: str, version_id: str = "-1") -> str:
    """Get a Zephyr Squad test cycle by its ID.

    Args:
        ctx: The FastMCP context.
        cycle_id: The test cycle ID.
        project_id: The Jira project ID (numeric).
        version_id: The version ID (default: -1 for unversioned).

    Returns:
        Test cycle details as a formatted string.
    """
    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.get_cycle(cycle_id, project_id, version_id)
        return _format_result("Squad Test Cycle", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error getting Squad cycle {cycle_id}: {e}"


async def squad_get_cycles(ctx: Context, project_id: str, version_id: str = "-1") -> str:
    """Get all Zephyr Squad test cycles for a project.

    Args:
        ctx: The FastMCP context.
        project_id: The Jira project ID (numeric).
        version_id: The version ID (default: -1 for unversioned).

    Returns:
        Test cycles list as a formatted string.
    """
    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.get_cycles(project_id, version_id)
        return _format_result("Squad Test Cycles", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error getting Squad cycles: {e}"


@check_write_access
async def squad_create_cycle(
    ctx: Context,
    project_id: str,
    name: str,
    version_id: str = "-1",
    description: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    build: str | None = None,
) -> str:
    """Create a new Zephyr Squad test cycle.

    Args:
        ctx: The FastMCP context.
        project_id: The Jira project ID (numeric).
        name: Name of the test cycle.
        version_id: The version ID (default: -1 for unversioned).
        description: Test cycle description.
        start_date: Start date (e.g., '15/Jan/25').
        end_date: End date (e.g., '30/Jan/25').
        build: Build label for the cycle.

    Returns:
        Created test cycle details as a formatted string.
    """
    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.create_cycle(
            project_id=project_id,
            name=name,
            version_id=version_id,
            description=description,
            start_date=start_date,
            end_date=end_date,
            build=build,
        )
        return _format_result("Created Squad Test Cycle", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error creating Squad cycle: {e}"


async def squad_get_execution(ctx: Context, execution_id: str) -> str:
    """Get a Zephyr Squad test execution by its ID.

    Args:
        ctx: The FastMCP context.
        execution_id: The test execution ID.

    Returns:
        Test execution details as a formatted string.
    """
    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.get_execution(execution_id)
        return _format_result("Squad Test Execution", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error getting Squad execution {execution_id}: {e}"


async def squad_get_executions_by_cycle(
    ctx: Context,
    project_id: str,
    cycle_id: str,
    version_id: str = "-1",
) -> str:
    """Get all Zephyr Squad test executions for a cycle.

    Args:
        ctx: The FastMCP context.
        project_id: The Jira project ID (numeric).
        cycle_id: The test cycle ID.
        version_id: The version ID (default: -1 for unversioned).

    Returns:
        Test executions list as a formatted string.
    """
    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.get_executions_by_cycle(project_id, cycle_id, version_id)
        return _format_result("Squad Test Executions", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error getting Squad executions for cycle {cycle_id}: {e}"


@check_write_access
async def squad_add_test_to_cycle(
    ctx: Context,
    cycle_id: str,
    project_id: str,
    issue_id: str,
    version_id: str = "-1",
) -> str:
    """Add a test (Jira issue) to a Zephyr Squad test cycle.

    Args:
        ctx: The FastMCP context.
        cycle_id: The test cycle ID.
        project_id: The Jira project ID (numeric).
        issue_id: The Jira issue ID (numeric) representing the test.
        version_id: The version ID (default: -1 for unversioned).

    Returns:
        Created execution details as a formatted string.
    """
    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.add_test_to_cycle(cycle_id, project_id, issue_id, version_id)
        return _format_result("Added Test to Squad Cycle", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error adding test to Squad cycle: {e}"


@check_write_access
async def squad_update_execution(
    ctx: Context,
    execution_id: str,
    status: str | None = None,
    comment: str | None = None,
    assigned_to: str | None = None,
) -> str:
    """Update a Zephyr Squad test execution.

    Args:
        ctx: The FastMCP context.
        execution_id: The test execution ID.
        status: Execution status (PASS, FAIL, WIP, BLOCKED, UNEXECUTED).
        comment: Comment for the execution.
        assigned_to: Account ID of user to assign.

    Returns:
        Updated test execution details as a formatted string.
    """
    if status and status.upper() not in SQUAD_EXECUTION_STATUSES:
        return f"Invalid status '{status}'. Valid statuses: {', '.join(SQUAD_EXECUTION_STATUSES.keys())}"

    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.update_execution(
            execution_id=execution_id,
            status=status,
            comment=comment,
            assigned_to=assigned_to,
        )
        return _format_result("Updated Squad Test Execution", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error updating Squad execution {execution_id}: {e}"


async def squad_zql_search(
    ctx: Context,
    zql_query: str,
    max_records: int = 50,
    offset: int = 0,
) -> str:
    """Execute a ZQL (Zephyr Query Language) search in Zephyr Squad.

    Args:
        ctx: The FastMCP context.
        zql_query: The ZQL query string (e.g., 'project = "PROJ" AND cycleName = "Regression"').
        max_records: Maximum number of records to return (default: 50).
        offset: Offset for pagination (default: 0).

    Returns:
        Search results as a formatted string.
    """
    try:
        fetcher = await get_squad_fetcher(ctx)
        result = fetcher.get_zql_search(zql_query, max_records, offset)
        return _format_result("Squad ZQL Search Results", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error executing ZQL search: {e}"


def _format_result(title: str, result: Any) -> str:
    """Format an API result for display."""
    import json

    if isinstance(result, dict):
        return f"## {title}\n```json\n{json.dumps(result, indent=2)}\n```"
    elif isinstance(result, list):
        return f"## {title}\n```json\n{json.dumps(result, indent=2)}\n```"
    return f"## {title}\n{result}"
