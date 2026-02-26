"""Tests for zephyr_mcp.squad.client module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.squad.client import API_PREFIX, ZephyrSquadClient
from zephyr_mcp.squad.config import ZephyrSquadConfig


def _make_config():
    return ZephyrSquadConfig(
        base_url="https://prod-api.zephyr4jiracloud.com/connect",
        access_key="test-ak",
        secret_key="test-sk",
        account_id="test-aid",
    )


class TestZephyrSquadClientInit:
    def test_sets_base_url(self):
        config = _make_config()
        client = ZephyrSquadClient(config)
        assert client.base_url == "https://prod-api.zephyr4jiracloud.com/connect"
        assert client.config is config

    def test_strips_trailing_slash(self):
        config = ZephyrSquadConfig(
            base_url="https://example.com/connect/",
            access_key="ak",
            secret_key="sk",
            account_id="aid",
        )
        client = ZephyrSquadClient(config)
        assert client.base_url == "https://example.com/connect"

    def test_session_content_type(self):
        client = ZephyrSquadClient(_make_config())
        assert client.session.headers["Content-Type"] == "application/json"


class TestGetAuthHeaders:
    def test_returns_jwt_and_access_key(self):
        client = ZephyrSquadClient(_make_config())
        headers = client._get_auth_headers("GET", "/public/rest/api/1.0/cycle")
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("JWT ")
        assert headers["zapiAccessKey"] == "test-ak"

    def test_passes_query_params(self):
        client = ZephyrSquadClient(_make_config())
        headers1 = client._get_auth_headers("GET", "/path")
        headers2 = client._get_auth_headers("GET", "/path", {"projectId": "123"})
        # Different query params produce different JWT tokens
        assert headers1["Authorization"] != headers2["Authorization"]


class TestRequest:
    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_get_success(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}
        client.session.request = MagicMock(return_value=mock_response)

        result = client.get("/cycle/123")
        assert result == {"id": "123"}
        client.session.request.assert_called_once()
        call_args = client.session.request.call_args
        assert call_args[0][0] == "GET"
        assert f"{API_PREFIX}/cycle/123" in call_args[0][1]

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_post_with_json(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "new-cycle"}
        client.session.request = MagicMock(return_value=mock_response)

        result = client.post("/cycle", json={"name": "Test Cycle"})
        assert result == {"id": "new-cycle"}
        call_args = client.session.request.call_args
        assert call_args[1]["json"] == {"name": "Test Cycle"}

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_put_request(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}
        client.session.request = MagicMock(return_value=mock_response)

        result = client.put("/cycle/123", json={"name": "Updated"})
        assert result == {"updated": True}

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_delete_request(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 204
        client.session.request = MagicMock(return_value=mock_response)

        result = client.delete("/cycle/123")
        assert result == {}

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_auth_error_401(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        client.session.request = MagicMock(return_value=mock_response)

        with pytest.raises(ZephyrAuthenticationError, match="401"):
            client.get("/cycle/123")

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_auth_error_403(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        client.session.request = MagicMock(return_value=mock_response)

        with pytest.raises(ZephyrAuthenticationError, match="403"):
            client.post("/cycle")

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_http_error_raises(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Internal Server Error")
        client.session.request = MagicMock(return_value=mock_response)

        with pytest.raises(requests.HTTPError):
            client.get("/cycle/123")

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_query_params_passed(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        client.session.request = MagicMock(return_value=mock_response)

        client.get("/cycles/search", query_params={"projectId": "10200", "versionId": "-1"})
        call_args = client.session.request.call_args
        assert call_args[1]["params"] == {"projectId": "10200", "versionId": "-1"}

    @patch("zephyr_mcp.squad.client.generate_jwt_token", return_value="fake-jwt")
    def test_custom_headers_merged(self, mock_jwt):
        client = ZephyrSquadClient(_make_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        client.session.request = MagicMock(return_value=mock_response)

        client.get("/cycle/1", headers={"X-Custom": "value"})
        call_args = client.session.request.call_args
        headers = call_args[1]["headers"]
        assert headers["X-Custom"] == "value"
        assert "Authorization" in headers
