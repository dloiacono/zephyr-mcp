"""Zephyr Scale Test Cycles mixin."""

import logging
from typing import Any

logger = logging.getLogger("mcp-zephyr")


class TestCyclesMixin:
    """Mixin providing test cycle operations for the Zephyr Scale API."""

    def get_test_cycle(self, test_cycle_key: str) -> dict[str, Any]:
        """Get a test cycle by key."""
        logger.debug(f"Getting test cycle: {test_cycle_key}")
        return self.client.get(f"/testcycles/{test_cycle_key}")

    def search_test_cycles(
        self,
        project_key: str,
        query: str | None = None,
        max_results: int = 50,
        start_at: int = 0,
    ) -> dict[str, Any]:
        """Search for test cycles in a project."""
        logger.debug(f"Searching test cycles in project {project_key}: query={query}")

        params: dict[str, Any] = {
            "projectKey": project_key,
            "maxResults": max_results,
            "startAt": start_at,
        }

        if query:
            params["query"] = query

        return self.client.get("/testcycles", params=params)

    def create_test_cycle(
        self,
        project_key: str,
        name: str,
        description: str | None = None,
        planned_start_date: str | None = None,
        planned_end_date: str | None = None,
        folder: str | None = None,
        jira_project_version: int | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new test cycle."""
        logger.debug(f"Creating test cycle in project {project_key}: name={name}")

        payload: dict[str, Any] = {
            "projectKey": project_key,
            "name": name,
        }

        if description:
            payload["description"] = description
        if planned_start_date:
            payload["plannedStartDate"] = planned_start_date
        if planned_end_date:
            payload["plannedEndDate"] = planned_end_date
        if folder:
            payload["folder"] = folder
        if jira_project_version is not None:
            payload["jiraProjectVersion"] = jira_project_version
        if custom_fields:
            payload["customFields"] = custom_fields

        return self.client.post("/testcycles", json=payload)

    def update_test_cycle(
        self,
        test_cycle_key: str,
        name: str | None = None,
        description: str | None = None,
        planned_start_date: str | None = None,
        planned_end_date: str | None = None,
        folder: str | None = None,
        jira_project_version: int | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an existing test cycle."""
        logger.debug(f"Updating test cycle: {test_cycle_key}")

        payload: dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if planned_start_date is not None:
            payload["plannedStartDate"] = planned_start_date
        if planned_end_date is not None:
            payload["plannedEndDate"] = planned_end_date
        if folder is not None:
            payload["folder"] = folder
        if jira_project_version is not None:
            payload["jiraProjectVersion"] = jira_project_version
        if custom_fields is not None:
            payload["customFields"] = custom_fields

        return self.client.put(f"/testcycles/{test_cycle_key}", json=payload)

    def delete_test_cycle(self, test_cycle_key: str) -> dict[str, Any]:
        """Delete a test cycle."""
        logger.debug(f"Deleting test cycle: {test_cycle_key}")
        return self.client.delete(f"/testcycles/{test_cycle_key}")

    def link_test_cycle_to_issue(self, test_cycle_key: str, issue_key: str) -> dict[str, Any]:
        """Link a test cycle to a Jira issue."""
        logger.debug(f"Linking test cycle {test_cycle_key} to issue {issue_key}")
        payload = {"issueKey": issue_key}
        return self.client.post(f"/testcycles/{test_cycle_key}/links/issues", json=payload)
