"""Zephyr Scale Test Cases mixin."""

import logging
from typing import Any

from zephyr_mcp.zephyr.constants import DEFAULT_TEST_CASE_FIELDS

logger = logging.getLogger("mcp-zephyr")


class TestCasesMixin:
    """Mixin providing test case operations for the Zephyr Scale API."""

    def get_test_case(self, test_case_key: str) -> dict[str, Any]:
        """Get a test case by key."""
        logger.debug(f"Getting test case: {test_case_key}")
        return self.client.get(f"/testcases/{test_case_key}")

    def search_test_cases(
        self,
        project_key: str,
        query: str | None = None,
        max_results: int = 50,
        start_at: int = 0,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search for test cases in a project."""
        logger.debug(f"Searching test cases in project {project_key}: query={query}")

        params: dict[str, Any] = {
            "projectKey": project_key,
            "maxResults": max_results,
            "startAt": start_at,
        }

        if query:
            params["query"] = query

        if fields:
            params["fields"] = ",".join(fields)
        else:
            params["fields"] = ",".join(DEFAULT_TEST_CASE_FIELDS)

        return self.client.get("/testcases", params=params)

    def create_test_case(
        self,
        project_key: str,
        name: str,
        objective: str | None = None,
        precondition: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        folder: str | None = None,
        labels: list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new test case."""
        logger.debug(f"Creating test case in project {project_key}: name={name}")

        payload: dict[str, Any] = {
            "projectKey": project_key,
            "name": name,
        }

        if objective:
            payload["objective"] = objective
        if precondition:
            payload["precondition"] = precondition
        if status:
            payload["status"] = status
        if priority:
            payload["priority"] = priority
        if folder:
            payload["folder"] = folder
        if labels:
            payload["labels"] = labels
        if custom_fields:
            payload["customFields"] = custom_fields

        return self.client.post("/testcases", json=payload)

    def update_test_case(
        self,
        test_case_key: str,
        name: str | None = None,
        objective: str | None = None,
        precondition: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        folder: str | None = None,
        labels: list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an existing test case."""
        logger.debug(f"Updating test case: {test_case_key}")

        payload: dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if objective is not None:
            payload["objective"] = objective
        if precondition is not None:
            payload["precondition"] = precondition
        if status is not None:
            payload["status"] = status
        if priority is not None:
            payload["priority"] = priority
        if folder is not None:
            payload["folder"] = folder
        if labels is not None:
            payload["labels"] = labels
        if custom_fields is not None:
            payload["customFields"] = custom_fields

        return self.client.put(f"/testcases/{test_case_key}", json=payload)

    def delete_test_case(self, test_case_key: str) -> dict[str, Any]:
        """Delete a test case."""
        logger.debug(f"Deleting test case: {test_case_key}")
        return self.client.delete(f"/testcases/{test_case_key}")

    def link_test_case_to_issue(self, test_case_key: str, issue_key: str) -> dict[str, Any]:
        """Link a test case to a Jira issue."""
        logger.debug(f"Linking test case {test_case_key} to issue {issue_key}")
        payload = {"issueKey": issue_key}
        return self.client.post(f"/testcases/{test_case_key}/links/issues", json=payload)
