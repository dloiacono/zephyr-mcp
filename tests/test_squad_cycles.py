"""Tests for zephyr_mcp.squad.cycles module."""

from unittest.mock import MagicMock

from zephyr_mcp.squad.cycles import SquadCyclesMixin


def _make_mixin():
    mixin = SquadCyclesMixin()
    mixin.client = MagicMock()
    return mixin


class TestGetCycle:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {"id": "1", "name": "Cycle 1"}

        result = mixin.get_cycle("1", "10200")
        mixin.client.get.assert_called_once_with("/cycle/1", query_params={"projectId": "10200", "versionId": "-1"})
        assert result == {"id": "1", "name": "Cycle 1"}

    def test_custom_version_id(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = {}

        mixin.get_cycle("1", "10200", version_id="5")
        mixin.client.get.assert_called_once_with("/cycle/1", query_params={"projectId": "10200", "versionId": "5"})


class TestGetCycles:
    def test_calls_client_get(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = [{"id": "1"}, {"id": "2"}]

        result = mixin.get_cycles("10200")
        mixin.client.get.assert_called_once_with("/cycles/search", query_params={"projectId": "10200", "versionId": "-1"})
        assert len(result) == 2

    def test_custom_version(self):
        mixin = _make_mixin()
        mixin.client.get.return_value = []

        mixin.get_cycles("10200", version_id="100")
        mixin.client.get.assert_called_once_with("/cycles/search", query_params={"projectId": "10200", "versionId": "100"})


class TestCreateCycle:
    def test_minimal_payload(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"id": "new-cycle"}

        result = mixin.create_cycle("10200", "Sprint 1")
        mixin.client.post.assert_called_once_with("/cycle", json={"projectId": "10200", "versionId": "-1", "name": "Sprint 1"})
        assert result == {"id": "new-cycle"}

    def test_full_payload(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {"id": "new-cycle"}

        mixin.create_cycle(
            project_id="10200",
            name="Sprint 1",
            version_id="5",
            description="Test cycle",
            start_date="15/Jan/25",
            end_date="30/Jan/25",
            build="1.0.0",
        )
        call_args = mixin.client.post.call_args
        payload = call_args[1]["json"]
        assert payload["projectId"] == "10200"
        assert payload["name"] == "Sprint 1"
        assert payload["versionId"] == "5"
        assert payload["description"] == "Test cycle"
        assert payload["startDate"] == "15/Jan/25"
        assert payload["endDate"] == "30/Jan/25"
        assert payload["build"] == "1.0.0"

    def test_optional_fields_excluded_when_none(self):
        mixin = _make_mixin()
        mixin.client.post.return_value = {}

        mixin.create_cycle("10200", "Cycle")
        payload = mixin.client.post.call_args[1]["json"]
        assert "description" not in payload
        assert "startDate" not in payload
        assert "endDate" not in payload
        assert "build" not in payload


class TestUpdateCycle:
    def test_update_name(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {"id": "1", "name": "Updated"}

        result = mixin.update_cycle("1", name="Updated")
        mixin.client.put.assert_called_once_with("/cycle/1", json={"name": "Updated"})
        assert result["name"] == "Updated"

    def test_update_all_fields(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_cycle("1", name="N", description="D", start_date="S", end_date="E", build="B")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload == {"name": "N", "description": "D", "startDate": "S", "endDate": "E", "build": "B"}

    def test_empty_update(self):
        mixin = _make_mixin()
        mixin.client.put.return_value = {}

        mixin.update_cycle("1")
        payload = mixin.client.put.call_args[1]["json"]
        assert payload == {}


class TestDeleteCycle:
    def test_calls_client_delete(self):
        mixin = _make_mixin()
        mixin.client.delete.return_value = {}

        result = mixin.delete_cycle("1")
        mixin.client.delete.assert_called_once_with("/cycle/1")
        assert result == {}
