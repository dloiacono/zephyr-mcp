"""Zephyr Squad test execution operations mixin."""

import logging
from typing import Any

logger = logging.getLogger("mcp-zephyr-squad")

SQUAD_EXECUTION_STATUSES = {
    "PASS": 1,
    "FAIL": 2,
    "WIP": 3,
    "BLOCKED": 4,
    "UNEXECUTED": -1,
}


class SquadExecutionsMixin:
    """Mixin providing test execution operations for the Zephyr Squad Cloud API."""

    def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Get a test execution by ID."""
        logger.debug(f"Getting Squad execution: {execution_id}")
        return self.client.get(f"/execution/{execution_id}")

    def get_executions_by_cycle(
        self,
        project_id: str,
        cycle_id: str,
        version_id: str = "-1",
    ) -> dict[str, Any]:
        """Get all executions for a cycle."""
        logger.debug(f"Getting Squad executions for cycle {cycle_id}")
        return self.client.get(
            f"/executions/search/cycle/{cycle_id}",
            query_params={"projectId": project_id, "versionId": version_id},
        )

    def add_test_to_cycle(
        self,
        cycle_id: str,
        project_id: str,
        issue_id: str,
        version_id: str = "-1",
    ) -> dict[str, Any]:
        """Add a test (Jira issue) to a test cycle, creating an execution."""
        logger.debug(f"Adding test {issue_id} to Squad cycle {cycle_id}")
        payload: dict[str, Any] = {
            "cycleId": cycle_id,
            "projectId": project_id,
            "versionId": version_id,
            "issueId": issue_id,
        }
        return self.client.post("/execution", json=payload)

    def update_execution(
        self,
        execution_id: str,
        status: str | None = None,
        comment: str | None = None,
        assigned_to: str | None = None,
    ) -> dict[str, Any]:
        """Update a test execution status."""
        logger.debug(f"Updating Squad execution: {execution_id}")

        payload: dict[str, Any] = {}

        if status is not None:
            status_upper = status.upper()
            if status_upper not in SQUAD_EXECUTION_STATUSES:
                raise ValueError(f"Invalid status '{status}'. Valid statuses: {', '.join(SQUAD_EXECUTION_STATUSES.keys())}")
            payload["status"] = SQUAD_EXECUTION_STATUSES[status_upper]
        if comment is not None:
            payload["comment"] = comment
        if assigned_to is not None:
            payload["assignedTo"] = assigned_to

        return self.client.put(f"/execution/{execution_id}", json=payload)

    def get_zql_search(
        self,
        zql_query: str,
        max_records: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Execute a ZQL (Zephyr Query Language) search."""
        logger.debug(f"Executing ZQL search: {zql_query}")
        return self.client.get(
            "/zql/executeSearch",
            query_params={
                "zqlQuery": zql_query,
                "maxRecords": str(max_records),
                "offset": str(offset),
            },
        )
