"""Tests for zephyr_mcp.zephyr.testexecutions module."""

from unittest.mock import MagicMock

from zephyr_mcp.zephyr.testexecutions import TestExecutionsMixin


def _make_mixin():
    mixin = TestExecutionsMixin()
    mixin.client = MagicMock()
    return mixin


class TestGetTestExecution:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"id": "12345", "statusName": "Pass"}
        result = mixin.get_test_execution("12345")
        mixin.client.get.assert_called_once_with("/testexecutions/12345")
        assert result["id"] == "12345"


class TestSearchTestExecutions:
    def test_basic_search(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_executions("PROJ")
        params = mixin.client.get.call_args[1]["params"]
        assert params["projectKey"] == "PROJ"

    def test_search_with_cycle(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_executions("PROJ", test_cycle_key="PROJ-R1")
        params = mixin.client.get.call_args[1]["params"]
        assert params["testCycle"] == "PROJ-R1"

    def test_search_with_case(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_executions("PROJ", test_case_key="PROJ-T1")
        params = mixin.client.get.call_args[1]["params"]
        assert params["testCase"] == "PROJ-T1"

    def test_search_with_pagination(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_executions("PROJ", max_results=25, start_at=50)
        params = mixin.client.get.call_args[1]["params"]
        assert params["maxResults"] == 25
        assert params["startAt"] == 50


class TestCreateTestExecution:
    def test_minimal_create(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"id": "999"}
        result = mixin.create_test_execution("PROJ", "PROJ-T1", "PROJ-R1")
        payload = mixin.client.post.call_args[1]["json"]
        assert payload["projectKey"] == "PROJ"
        assert payload["testCaseKey"] == "PROJ-T1"
        assert payload["testCycleKey"] == "PROJ-R1"
        assert result["id"] == "999"

    def test_full_create(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"id": "1000"}
        mixin.create_test_execution(
            "PROJ",
            "PROJ-T1",
            "PROJ-R1",
            status_name="Pass",
            environment="Production",
            comment="All good",
            execution_time=5000,
            assigned_to="user@example.com",
            custom_fields={"cf1": "val1"},
        )
        payload = mixin.client.post.call_args[1]["json"]
        assert payload["statusName"] == "Pass"
        assert payload["environment"] == "Production"
        assert payload["comment"] == "All good"
        assert payload["executionTime"] == 5000
        assert payload["assignedTo"] == "user@example.com"
        assert payload["customFields"] == {"cf1": "val1"}

    def test_optional_fields_not_included(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"id": "1001"}
        mixin.create_test_execution("PROJ", "PROJ-T1", "PROJ-R1")
        payload = mixin.client.post.call_args[1]["json"]
        assert "statusName" not in payload
        assert "environment" not in payload


class TestUpdateTestExecution:
    def test_update_status(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"id": "12345"}
        mixin.update_test_execution("12345", status_name="Fail")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["statusName"] == "Fail"

    def test_update_multiple_fields(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"id": "12345"}
        mixin.update_test_execution("12345", status_name="Pass", comment="Retested", execution_time=3000)
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["statusName"] == "Pass"
        assert payload["comment"] == "Retested"
        assert payload["executionTime"] == 3000

    def test_update_empty_payload(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"id": "12345"}
        mixin.update_test_execution("12345")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload == {}


class TestDeleteTestExecution:
    def test_delete(self):
        mixin = _make_mixin()
        mixin.client.delete.return_value = {}
        mixin.delete_test_execution("12345")
        mixin.client.delete.assert_called_once_with("/testexecutions/12345")


class TestGetTestExecutionResults:
    def test_get_results(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [{"stepIndex": 1}]}
        result = mixin.get_test_execution_results("12345")
        params = mixin.client.get.call_args[1]["params"]
        assert params["maxResults"] == 50
        assert params["startAt"] == 0
        assert result["values"][0]["stepIndex"] == 1

    def test_get_results_with_pagination(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": []}
        mixin.get_test_execution_results("12345", max_results=10, start_at=5)
        params = mixin.client.get.call_args[1]["params"]
        assert params["maxResults"] == 10
        assert params["startAt"] == 5
