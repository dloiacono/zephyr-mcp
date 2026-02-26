"""Tests for zephyr_mcp.zephyr.testcases module."""

from unittest.mock import MagicMock

from zephyr_mcp.zephyr.testcases import TestCasesMixin


def _make_mixin():
    mixin = TestCasesMixin()
    mixin.client = MagicMock()
    return mixin


class TestGetTestCase:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"key": "PROJ-T1", "name": "Test Case 1"}
        result = mixin.get_test_case("PROJ-T1")
        mixin.client.get.assert_called_once_with("/testcases/PROJ-T1")
        assert result["key"] == "PROJ-T1"


class TestSearchTestCases:
    def test_basic_search(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cases("PROJ")
        call_kwargs = mixin.client.get.call_args
        assert call_kwargs[1]["params"]["projectKey"] == "PROJ"

    def test_search_with_query(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cases("PROJ", query="login")
        params = mixin.client.get.call_args[1]["params"]
        assert params["query"] == "login"

    def test_search_with_custom_fields(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cases("PROJ", fields=["key", "name"])
        params = mixin.client.get.call_args[1]["params"]
        assert params["fields"] == "key,name"

    def test_search_with_pagination(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cases("PROJ", max_results=10, start_at=5)
        params = mixin.client.get.call_args[1]["params"]
        assert params["maxResults"] == 10
        assert params["startAt"] == 5

    def test_search_default_fields(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"values": [], "total": 0}
        mixin.search_test_cases("PROJ")
        params = mixin.client.get.call_args[1]["params"]
        assert "fields" in params
        assert "key" in params["fields"]


class TestCreateTestCase:
    def test_minimal_create(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"key": "PROJ-T2"}
        result = mixin.create_test_case("PROJ", "My Test Case")
        payload = mixin.client.post.call_args[1]["json"]
        assert payload["projectKey"] == "PROJ"
        assert payload["name"] == "My Test Case"
        assert result["key"] == "PROJ-T2"

    def test_full_create(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"key": "PROJ-T3"}
        mixin.create_test_case(
            "PROJ",
            "Full Test",
            objective="Test login",
            precondition="User exists",
            status="Draft",
            priority="High",
            folder="/Login",
            labels=["smoke", "regression"],
            custom_fields={"cf1": "val1"},
        )
        payload = mixin.client.post.call_args[1]["json"]
        assert payload["objective"] == "Test login"
        assert payload["precondition"] == "User exists"
        assert payload["status"] == "Draft"
        assert payload["priority"] == "High"
        assert payload["folder"] == "/Login"
        assert payload["labels"] == ["smoke", "regression"]
        assert payload["customFields"] == {"cf1": "val1"}

    def test_optional_fields_not_included_when_none(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"key": "PROJ-T4"}
        mixin.create_test_case("PROJ", "Simple")
        payload = mixin.client.post.call_args[1]["json"]
        assert "objective" not in payload
        assert "precondition" not in payload
        assert "status" not in payload


class TestUpdateTestCase:
    def test_update_name(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"key": "PROJ-T1"}
        mixin.update_test_case("PROJ-T1", name="Updated Name")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["name"] == "Updated Name"

    def test_update_multiple_fields(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"key": "PROJ-T1"}
        mixin.update_test_case("PROJ-T1", name="New", status="Approved", priority="Low")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload["name"] == "New"
        assert payload["status"] == "Approved"
        assert payload["priority"] == "Low"

    def test_update_empty_payload_when_no_changes(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"key": "PROJ-T1"}
        mixin.update_test_case("PROJ-T1")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload == {}


class TestDeleteTestCase:
    def test_delete(self):
        mixin = _make_mixin()
        mixin.client.delete.return_value = {}
        mixin.delete_test_case("PROJ-T1")
        mixin.client.delete.assert_called_once_with("/testcases/PROJ-T1")


class TestLinkTestCaseToIssue:
    def test_link(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {}
        mixin.link_test_case_to_issue("PROJ-T1", "PROJ-123")
        call_args = mixin.client.post.call_args
        assert "/testcases/PROJ-T1/links/issues" in call_args[0][0]
        assert call_args[1]["json"] == {"issueKey": "PROJ-123"}
