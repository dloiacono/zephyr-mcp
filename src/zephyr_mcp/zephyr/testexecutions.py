"""Zephyr Scale Test Executions mixin."""

import logging
from typing import Any

logger = logging.getLogger("mcp-zephyr")


class TestExecutionsMixin:
    """Mixin providing test execution operations for the Zephyr Scale API."""

    def get_test_execution(self, test_execution_id: str) -> dict[str, Any]:
        """Get a test execution by ID."""
        logger.debug(f"Getting test execution: {test_execution_id}")
        return self.client.get(f"/testexecutions/{test_execution_id}")

    def search_test_executions(
        self,
        project_key: str,
        test_cycle_key: str | None = None,
        test_case_key: str | None = None,
        max_results: int = 50,
        start_at: int = 0,
    ) -> dict[str, Any]:
        """Search for test executions in a project."""
        logger.debug(f"Searching test executions in project {project_key}")

        params: dict[str, Any] = {
            "projectKey": project_key,
            "maxResults": max_results,
            "startAt": start_at,
        }

        if test_cycle_key:
            params["testCycle"] = test_cycle_key
        if test_case_key:
            params["testCase"] = test_case_key

        return self.client.get("/testexecutions", params=params)

    def create_test_execution(
        self,
        project_key: str,
        test_case_key: str,
        test_cycle_key: str,
        status_name: str | None = None,
        environment: str | None = None,
        comment: str | None = None,
        execution_time: int | None = None,
        assigned_to: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new test execution."""
        logger.debug(f"Creating test execution: testCase={test_case_key}, testCycle={test_cycle_key}")

        payload: dict[str, Any] = {
            "projectKey": project_key,
            "testCaseKey": test_case_key,
            "testCycleKey": test_cycle_key,
        }

        if status_name:
            payload["statusName"] = status_name
        if environment:
            payload["environment"] = environment
        if comment:
            payload["comment"] = comment
        if execution_time is not None:
            payload["executionTime"] = execution_time
        if assigned_to:
            payload["assignedTo"] = assigned_to
        if custom_fields:
            payload["customFields"] = custom_fields

        return self.client.post("/testexecutions", json=payload)

    def update_test_execution(
        self,
        test_execution_id: str,
        status_name: str | None = None,
        environment: str | None = None,
        comment: str | None = None,
        execution_time: int | None = None,
        assigned_to: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an existing test execution."""
        logger.debug(f"Updating test execution: {test_execution_id}")

        payload: dict[str, Any] = {}

        if status_name is not None:
            payload["statusName"] = status_name
        if environment is not None:
            payload["environment"] = environment
        if comment is not None:
            payload["comment"] = comment
        if execution_time is not None:
            payload["executionTime"] = execution_time
        if assigned_to is not None:
            payload["assignedTo"] = assigned_to
        if custom_fields is not None:
            payload["customFields"] = custom_fields

        return self.client.put(f"/testexecutions/{test_execution_id}", json=payload)

    def delete_test_execution(self, test_execution_id: str) -> dict[str, Any]:
        """Delete a test execution."""
        logger.debug(f"Deleting test execution: {test_execution_id}")
        return self.client.delete(f"/testexecutions/{test_execution_id}")

    def get_test_execution_results(
        self,
        test_execution_id: str,
        max_results: int = 50,
        start_at: int = 0,
    ) -> dict[str, Any]:
        """Get test execution results."""
        logger.debug(f"Getting results for test execution: {test_execution_id}")
        params: dict[str, Any] = {
            "maxResults": max_results,
            "startAt": start_at,
        }
        return self.client.get(f"/testexecutions/{test_execution_id}/teststeps", params=params)
