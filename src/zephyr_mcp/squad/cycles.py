"""Zephyr Squad test cycle operations mixin."""

import logging
from typing import Any

logger = logging.getLogger("mcp-zephyr-squad")


class SquadCyclesMixin:
    """Mixin providing test cycle operations for the Zephyr Squad Cloud API."""

    def get_cycle(self, cycle_id: str, project_id: str, version_id: str = "-1") -> dict[str, Any]:
        """Get a test cycle by ID."""
        logger.debug(f"Getting Squad cycle: {cycle_id}")
        return self.client.get(f"/cycle/{cycle_id}", query_params={"projectId": project_id, "versionId": version_id})

    def get_cycles(self, project_id: str, version_id: str = "-1") -> dict[str, Any]:
        """Get all test cycles for a project and version."""
        logger.debug(f"Getting Squad cycles for project {project_id}, version {version_id}")
        return self.client.get("/cycles/search", query_params={"projectId": project_id, "versionId": version_id})

    def create_cycle(
        self,
        project_id: str,
        name: str,
        version_id: str = "-1",
        description: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        build: str | None = None,
    ) -> dict[str, Any]:
        """Create a new test cycle."""
        logger.debug(f"Creating Squad cycle in project {project_id}: name={name}")

        payload: dict[str, Any] = {
            "projectId": project_id,
            "versionId": version_id,
            "name": name,
        }

        if description:
            payload["description"] = description
        if start_date:
            payload["startDate"] = start_date
        if end_date:
            payload["endDate"] = end_date
        if build:
            payload["build"] = build

        return self.client.post("/cycle", json=payload)

    def update_cycle(
        self,
        cycle_id: str,
        name: str | None = None,
        description: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        build: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing test cycle."""
        logger.debug(f"Updating Squad cycle: {cycle_id}")

        payload: dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if start_date is not None:
            payload["startDate"] = start_date
        if end_date is not None:
            payload["endDate"] = end_date
        if build is not None:
            payload["build"] = build

        return self.client.put(f"/cycle/{cycle_id}", json=payload)

    def delete_cycle(self, cycle_id: str) -> dict[str, Any]:
        """Delete a test cycle."""
        logger.debug(f"Deleting Squad cycle: {cycle_id}")
        return self.client.delete(f"/cycle/{cycle_id}")
