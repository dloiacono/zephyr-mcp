"""Tests for zephyr_mcp.squad.executions module."""

from unittest.mock import MagicMock

import pytest

from zephyr_mcp.squad.executions import SQUAD_EXECUTION_STATUSES, SquadExecutionsMixin


def _make_mixin():
    mixin = SquadExecutionsMixin()
    mixin.client = MagicMock()
    return mixin


class TestExecutionStatuses:
    def test_status_mapping(self):
        assert SQUAD_EXECUTION_STATUSES["PASS"] == 1
        assert SQUAD_EXECUTION_STATUSES["FAIL"] == 2
        assert SQUAD_EXECUTION_STATUSES["WIP"] == 3
        assert SQUAD_EXECUTION_STATUSES["BLOCKED"] == 4
        assert SQUAD_EXECUTION_STATUSES["UNEXECUTED"] == -1


class TestGetExecution:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"id": "100", "status": {"id": 1}}

        result = mixin.get_execution("100")
        mixin.client.get.assert_called_once_with("/execution/100")
        assert result["id"] == "100"


class TestGetExecutionsByCycle:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"executions": []}

        result = mixin.get_executions_by_cycle("10200", "5")
        mixin.client.get.assert_called_once_with(
            "/executions/search/cycle/5",
            query_params={"projectId": "10200", "versionId": "-1"},
        )
        assert "executions" in result

    def test_custom_version(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {}

        mixin.get_executions_by_cycle("10200", "5", version_id="100")
        mixin.client.get.assert_called_once_with(
            "/executions/search/cycle/5",
            query_params={"projectId": "10200", "versionId": "100"},
        )


class TestAddTestToCycle:
    def test_calls_client_post(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"id": "200"}

        result = mixin.add_test_to_cycle("5", "10200", "99999")
        mixin.client.post.assert_called_once_with(
            "/execution",
            json={"cycleId": "5", "projectId": "10200", "versionId": "-1", "issueId": "99999"},
        )
        assert result == {"id": "200"}

    def test_custom_version(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {}

        mixin.add_test_to_cycle("5", "10200", "99999", version_id="100")
        payload = mixin.client.post.call_args[1]["json"]
        assert payload["versionId"] == "100"


class TestUpdateExecution:
    def test_update_status_pass(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"id": "100", "status": {"id": 1}}

        result = mixin.update_execution("100", status="PASS")
        mixin.client.put.assert_called_once_with("/execution/100", json={"status": 1})
        assert result["id"] == "100"

    def test_update_status_fail(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_execution("100", status="fail")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["status"] == 2

    def test_update_status_case_insensitive(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_execution("100", status="Blocked")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["status"] == 4

    def test_invalid_status_raises(self):
        mixin = _make_mixin()
        with pytest.raises(ValueError, match="Invalid status"):
            mixin.update_execution("100", status="INVALID")

    def test_update_comment(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_execution("100", comment="Test passed")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["comment"] == "Test passed"

    def test_update_assigned_to(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_execution("100", assigned_to="user-id-123")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["assignedTo"] == "user-id-123"

    def test_update_all_fields(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_execution("100", status="WIP", comment="In progress", assigned_to="user-123")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload == {"status": 3, "comment": "In progress", "assignedTo": "user-123"}

    def test_empty_update(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_execution("100")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload == {}


class TestGetZqlSearch:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"executions": [], "totalCount": 0}

        result = mixin.get_zql_search('project = "PROJ"')
        mixin.client.get.assert_called_once_with(
            "/zql/executeSearch",
            query_params={"zqlQuery": 'project = "PROJ"', "maxRecords": "50", "offset": "0"},
        )
        assert "totalCount" in result

    def test_custom_pagination(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {}

        mixin.get_zql_search("query", max_records=10, offset=20)
        query_params = mixin.client.get.call_args[1]["query_params"]
        assert query_params["maxRecords"] == "10"
        assert query_params["offset"] == "20"
