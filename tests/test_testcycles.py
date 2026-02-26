"""Tests for zephyr_mcp.zephyr.testcycles module."""

from unittest.mock import MagicMock

from zephyr_mcp.zephyr.testcycles import TestCyclesMixin


def _make_mixin():
    mixin = TestCyclesMixin()
    mixin.client = MagicMock()
    return mixin


class TestGetTestCycle:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"key": "PROJ-R1", "name": "Cycle 1"}
        result = mixin.get_test_cycle("PROJ-R1")
        mixin.client.get.assert_called_once_with("/testcycles/PROJ-R1")
        assert result["key"] == "PROJ-R1"


class TestSearchTestCycles:
    def test_basic_search(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cycles("PROJ")
        params = mixin.client.get.call_args[1]["params"]
        assert params["projectKey"] == "PROJ"

    def test_search_with_query(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cycles("PROJ", query="sprint 1")
        params = mixin.client.get.call_args[1]["params"]
        assert params["query"] == "sprint 1"

    def test_search_with_pagination(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cycles("PROJ", max_results=20, start_at=10)
        params = mixin.client.get.call_args[1]["params"]
        assert params["maxResults"] == 20
        assert params["startAt"] == 10


class TestCreateTestCycle:
    def test_minimal_create(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"key": "PROJ-R2"}
        result = mixin.create_test_cycle("PROJ", "Sprint 1 Cycle")
        payload = mixin.client.post.call_args[1]["json"]
        assert payload["projectKey"] == "PROJ"
        assert payload["name"] == "Sprint 1 Cycle"
        assert result["key"] == "PROJ-R2"

    def test_full_create(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"key": "PROJ-R3"}
        mixin.create_test_cycle(
            "PROJ",
            "Full Cycle",
            description="Description",
            planned_start_date="2025-01-01T00:00:00Z",
            planned_end_date="2025-01-31T00:00:00Z",
            folder="/Regression",
            jira_project_version=10001,
            custom_fields={"cf1": "val1"},
        )
        payload = mixin.client.post.call_args[1]["json"]
        assert payload["description"] == "Description"
        assert payload["plannedStartDate"] == "2025-01-01T00:00:00Z"
        assert payload["plannedEndDate"] == "2025-01-31T00:00:00Z"
        assert payload["folder"] == "/Regression"
        assert payload["jiraProjectVersion"] == 10001
        assert payload["customFields"] == {"cf1": "val1"}

    def test_optional_fields_not_included(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"key": "PROJ-R4"}
        mixin.create_test_cycle("PROJ", "Simple")
        payload = mixin.client.post.call_args[1]["json"]
        assert "description" not in payload
        assert "folder" not in payload


class TestUpdateTestCycle:
    def test_update_name(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"key": "PROJ-R1"}
        mixin.update_test_cycle("PROJ-R1", name="Updated Cycle")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["name"] == "Updated Cycle"

    def test_update_multiple_fields(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"key": "PROJ-R1"}
        mixin.update_test_cycle("PROJ-R1", name="New", description="Desc", folder="/New")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["name"] == "New"
        assert payload["description"] == "Desc"
        assert payload["folder"] == "/New"

    def test_update_empty_payload(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"key": "PROJ-R1"}
        mixin.update_test_cycle("PROJ-R1")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload == {}


class TestDeleteTestCycle:
    def test_delete(self):
        mixin = _make_mixin()
        mixin.client.delete.return_value = {}
        mixin.delete_test_cycle("PROJ-R1")
        mixin.client.delete.assert_called_once_with("/testcycles/PROJ-R1")


class TestLinkTestCycleToIssue:
    def test_link(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {}
        mixin.link_test_cycle_to_issue("PROJ-R1", "PROJ-123")
        call_args = mixin.client.post.call_args
        assert "/testcycles/PROJ-R1/links/issues" in call_args[0][0]
        assert call_args[1]["json"] == {"issueKey": "PROJ-123"}
