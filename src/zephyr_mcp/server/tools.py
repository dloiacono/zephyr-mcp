"""FastMCP tool definitions for the Zephyr Scale MCP server."""

import logging
from typing import Any

from fastmcp import Context

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.server.dependencies import get_zephyr_fetcher
from zephyr_mcp.utils.decorators import check_write_access
from zephyr_mcp.zephyr.constants import TEST_CASE_PRIORITIES, TEST_CASE_STATUSES, TEST_EXECUTION_STATUSES

logger = logging.getLogger("mcp-zephyr")


async def zephyr_get_test_case(ctx: Context, test_case_key: str) -> str:
    """Get a Zephyr Scale test case by its key.

    Args:
        ctx: The FastMCP context.
        test_case_key: The test case key (e.g., 'PROJ-T123').

    Returns:
        Test case details as a formatted string.
    """
    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.get_test_case(test_case_key)
        return _format_result("Test Case", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error getting test case {test_case_key}: {e}"


async def zephyr_search_test_cases(
    ctx: Context,
    project_key: str,
    query: str | None = None,
    max_results: int = 50,
    start_at: int = 0,
) -> str:
    """Search for Zephyr Scale test cases in a project.

    Args:
        ctx: The FastMCP context.
        project_key: The Jira project key (e.g., 'PROJ').
        query: Optional search query string.
        max_results: Maximum number of results to return (default: 50).
        start_at: Index of the first result to return (default: 0).

    Returns:
        Search results as a formatted string.
    """
    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.search_test_cases(project_key, query=query, max_results=max_results, start_at=start_at)
        return _format_result("Test Cases Search", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error searching test cases: {e}"


@check_write_access
async def zephyr_create_test_case(
    ctx: Context,
    project_key: str,
    name: str,
    objective: str | None = None,
    precondition: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    folder: str | None = None,
    labels: list[str] | None = None,
) -> str:
    """Create a new Zephyr Scale test case.

    Args:
        ctx: The FastMCP context.
        project_key: The Jira project key (e.g., 'PROJ').
        name: Name of the test case.
        objective: Test case objective/description.
        precondition: Test case preconditions.
        status: Test case status (Approved, Draft, Deprecated).
        priority: Test case priority (High, Normal, Low).
        folder: Folder path for the test case.
        labels: List of labels to assign.

    Returns:
        Created test case details as a formatted string.
    """
    if status and status not in TEST_CASE_STATUSES:
        return f"Invalid status '{status}'. Valid statuses: {', '.join(TEST_CASE_STATUSES)}"
    if priority and priority not in TEST_CASE_PRIORITIES:
        return f"Invalid priority '{priority}'. Valid priorities: {', '.join(TEST_CASE_PRIORITIES)}"

    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.create_test_case(
            project_key=project_key,
            name=name,
            objective=objective,
            precondition=precondition,
            status=status,
            priority=priority,
            folder=folder,
            labels=labels,
        )
        return _format_result("Created Test Case", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error creating test case: {e}"


@check_write_access
async def zephyr_update_test_case(
    ctx: Context,
    test_case_key: str,
    name: str | None = None,
    objective: str | None = None,
    precondition: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    folder: str | None = None,
    labels: list[str] | None = None,
) -> str:
    """Update an existing Zephyr Scale test case.

    Args:
        ctx: The FastMCP context.
        test_case_key: The test case key (e.g., 'PROJ-T123').
        name: New name for the test case.
        objective: New objective/description.
        precondition: New preconditions.
        status: New status (Approved, Draft, Deprecated).
        priority: New priority (High, Normal, Low).
        folder: New folder path.
        labels: New list of labels.

    Returns:
        Updated test case details as a formatted string.
    """
    if status and status not in TEST_CASE_STATUSES:
        return f"Invalid status '{status}'. Valid statuses: {', '.join(TEST_CASE_STATUSES)}"
    if priority and priority not in TEST_CASE_PRIORITIES:
        return f"Invalid priority '{priority}'. Valid priorities: {', '.join(TEST_CASE_PRIORITIES)}"

    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.update_test_case(
            test_case_key=test_case_key,
            name=name,
            objective=objective,
            precondition=precondition,
            status=status,
            priority=priority,
            folder=folder,
            labels=labels,
        )
        return _format_result("Updated Test Case", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error updating test case {test_case_key}: {e}"


async def zephyr_get_test_cycle(ctx: Context, test_cycle_key: str) -> str:
    """Get a Zephyr Scale test cycle by its key.

    Args:
        ctx: The FastMCP context.
        test_cycle_key: The test cycle key (e.g., 'PROJ-R123').

    Returns:
        Test cycle details as a formatted string.
    """
    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.get_test_cycle(test_cycle_key)
        return _format_result("Test Cycle", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error getting test cycle {test_cycle_key}: {e}"


@check_write_access
async def zephyr_create_test_cycle(
    ctx: Context,
    project_key: str,
    name: str,
    description: str | None = None,
    planned_start_date: str | None = None,
    planned_end_date: str | None = None,
    folder: str | None = None,
    jira_project_version: int | None = None,
) -> str:
    """Create a new Zephyr Scale test cycle.

    Args:
        ctx: The FastMCP context.
        project_key: The Jira project key (e.g., 'PROJ').
        name: Name of the test cycle.
        description: Test cycle description.
        planned_start_date: Planned start date (ISO 8601 format).
        planned_end_date: Planned end date (ISO 8601 format).
        folder: Folder path for the test cycle.
        jira_project_version: Jira project version ID.

    Returns:
        Created test cycle details as a formatted string.
    """
    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.create_test_cycle(
            project_key=project_key,
            name=name,
            description=description,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            folder=folder,
            jira_project_version=jira_project_version,
        )
        return _format_result("Created Test Cycle", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error creating test cycle: {e}"


async def zephyr_get_test_execution(ctx: Context, test_execution_id: str) -> str:
    """Get a Zephyr Scale test execution by its ID.

    Args:
        ctx: The FastMCP context.
        test_execution_id: The test execution ID.

    Returns:
        Test execution details as a formatted string.
    """
    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.get_test_execution(test_execution_id)
        return _format_result("Test Execution", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error getting test execution {test_execution_id}: {e}"


@check_write_access
async def zephyr_create_test_execution(
    ctx: Context,
    project_key: str,
    test_case_key: str,
    test_cycle_key: str,
    status_name: str | None = None,
    environment: str | None = None,
    comment: str | None = None,
    execution_time: int | None = None,
    assigned_to: str | None = None,
) -> str:
    """Create a new Zephyr Scale test execution.

    Args:
        ctx: The FastMCP context.
        project_key: The Jira project key (e.g., 'PROJ').
        test_case_key: The test case key (e.g., 'PROJ-T123').
        test_cycle_key: The test cycle key (e.g., 'PROJ-R123').
        status_name: Execution status (Pass, Fail, Blocked, Not Executed, In Progress).
        environment: Execution environment.
        comment: Comment for the execution.
        execution_time: Execution time in milliseconds.
        assigned_to: User assigned to the execution.

    Returns:
        Created test execution details as a formatted string.
    """
    if status_name and status_name not in TEST_EXECUTION_STATUSES:
        return f"Invalid status '{status_name}'. Valid statuses: {', '.join(TEST_EXECUTION_STATUSES)}"

    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.create_test_execution(
            project_key=project_key,
            test_case_key=test_case_key,
            test_cycle_key=test_cycle_key,
            status_name=status_name,
            environment=environment,
            comment=comment,
            execution_time=execution_time,
            assigned_to=assigned_to,
        )
        return _format_result("Created Test Execution", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error creating test execution: {e}"


@check_write_access
async def zephyr_update_test_execution(
    ctx: Context,
    test_execution_id: str,
    status_name: str | None = None,
    environment: str | None = None,
    comment: str | None = None,
    execution_time: int | None = None,
    assigned_to: str | None = None,
) -> str:
    """Update an existing Zephyr Scale test execution.

    Args:
        ctx: The FastMCP context.
        test_execution_id: The test execution ID.
        status_name: New execution status (Pass, Fail, Blocked, Not Executed, In Progress).
        environment: New execution environment.
        comment: New comment for the execution.
        execution_time: New execution time in milliseconds.
        assigned_to: New user assigned to the execution.

    Returns:
        Updated test execution details as a formatted string.
    """
    if status_name and status_name not in TEST_EXECUTION_STATUSES:
        return f"Invalid status '{status_name}'. Valid statuses: {', '.join(TEST_EXECUTION_STATUSES)}"

    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.update_test_execution(
            test_execution_id=test_execution_id,
            status_name=status_name,
            environment=environment,
            comment=comment,
            execution_time=execution_time,
            assigned_to=assigned_to,
        )
        return _format_result("Updated Test Execution", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error updating test execution {test_execution_id}: {e}"


@check_write_access
async def zephyr_link_test_case_to_issue(ctx: Context, test_case_key: str, issue_key: str) -> str:
    """Link a Zephyr Scale test case to a Jira issue.

    Args:
        ctx: The FastMCP context.
        test_case_key: The test case key (e.g., 'PROJ-T123').
        issue_key: The Jira issue key (e.g., 'PROJ-123').

    Returns:
        Link result as a formatted string.
    """
    try:
        fetcher = await get_zephyr_fetcher(ctx)
        result = fetcher.link_test_case_to_issue(test_case_key, issue_key)
        return _format_result("Linked Test Case to Issue", result)
    except ZephyrAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Error linking test case {test_case_key} to issue {issue_key}: {e}"


def _format_result(title: str, result: Any) -> str:
    """Format an API result for display."""
    import json

    if isinstance(result, dict):
        return f"## {title}\n```json\n{json.dumps(result, indent=2)}\n```"
    elif isinstance(result, list):
        return f"## {title}\n```json\n{json.dumps(result, indent=2)}\n```"
    return f"## {title}\n{result}"
