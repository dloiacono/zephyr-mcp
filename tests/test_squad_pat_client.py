"""Tests for zephyr_mcp.squad.pat_client module."""

from unittest.mock import MagicMock

import pytest
import requests

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.squad.config import AUTH_TYPE_PAT, ZephyrSquadConfig
from zephyr_mcp.squad.pat_client import ZAPI_PREFIX, ZephyrSquadPatClient


def _make_pat_config(email: str | None = None) -> ZephyrSquadConfig:
    return ZephyrSquadConfig(
        auth_type=AUTH_TYPE_PAT,
        jira_base_url="https://jira.example.com",
        pat_token="my-pat-token",
        jira_email=email,
    )


class TestZephyrSquadPatClientInit:
    def test_sets_base_url(self):
        config = _make_pat_config()
        client = ZephyrSquadPatClient(config)
        assert client.base_url == "https://jira.example.com"
        assert client.config is config

    def test_strips_trailing_slash(self):
        config = ZephyrSquadConfig(
            auth_type=AUTH_TYPE_PAT,
            jira_base_url="https://jira.example.com/",
            pat_token="my-pat-token",
        )
        client = ZephyrSquadPatClient(config)
        assert client.base_url == "https://jira.example.com"

    def test_session_content_type(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        assert client.session.headers["Content-Type"] == "application/json"


class TestPatAuthSetup:
    def test_bearer_auth_when_no_email(self):
        client = ZephyrSquadPatClient(_make_pat_config(email=None))
        assert client.session.headers.get("Authorization") == "Bearer my-pat-token"
        assert client.session.auth is None

    def test_basic_auth_when_email_provided(self):
        client = ZephyrSquadPatClient(_make_pat_config(email="user@example.com"))
        assert client.session.auth == ("user@example.com", "my-pat-token")
        assert "Authorization" not in client.session.headers


class TestPatRequest:
    def test_get_success(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}
        client.session.request = MagicMock(return_value=mock_response)

        result = client.get("/cycle/123")
        assert result == {"id": "123"}
        client.session.request.assert_called_once()
        call_args = client.session.request.call_args
        assert call_args[0][0] == "GET"
        assert f"{ZAPI_PREFIX}/cycle/123" in call_args[0][1]
        assert call_args[0][1] == f"https://jira.example.com{ZAPI_PREFIX}/cycle/123"

    def test_post_with_json(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "new-cycle"}
        client.session.request = MagicMock(return_value=mock_response)

        result = client.post("/cycle", json={"name": "Test Cycle"})
        assert result == {"id": "new-cycle"}
        call_args = client.session.request.call_args
        assert call_args[1]["json"] == {"name": "Test Cycle"}

    def test_put_request(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}
        client.session.request = MagicMock(return_value=mock_response)

        result = client.put("/cycle/123", json={"name": "Updated"})
        assert result == {"updated": True}

    def test_delete_request_204(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 204
        client.session.request = MagicMock(return_value=mock_response)

        result = client.delete("/cycle/123")
        assert result == {}

    def test_auth_error_401(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        client.session.request = MagicMock(return_value=mock_response)

        with pytest.raises(ZephyrAuthenticationError, match="401"):
            client.get("/cycle/123")

    def test_auth_error_403(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        client.session.request = MagicMock(return_value=mock_response)

        with pytest.raises(ZephyrAuthenticationError, match="403"):
            client.post("/cycle")

    def test_http_error_raises(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Internal Server Error")
        client.session.request = MagicMock(return_value=mock_response)

        with pytest.raises(requests.HTTPError):
            client.get("/cycle/123")

    def test_query_params_passed(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        client.session.request = MagicMock(return_value=mock_response)

        client.get("/cycles/search", query_params={"projectId": "10200", "versionId": "-1"})
        call_args = client.session.request.call_args
        assert call_args[1]["params"] == {"projectId": "10200", "versionId": "-1"}

    def test_custom_headers_merged(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        client.session.request = MagicMock(return_value=mock_response)

        client.get("/cycle/1", headers={"X-Custom": "value"})
        call_args = client.session.request.call_args
        headers = call_args[1]["headers"]
        assert headers["X-Custom"] == "value"

    def test_no_jwt_headers_in_pat_requests(self):
        client = ZephyrSquadPatClient(_make_pat_config())
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        client.session.request = MagicMock(return_value=mock_response)

        client.get("/cycle/1")
        call_args = client.session.request.call_args
        headers = call_args[1]["headers"]
        assert "zapiAccessKey" not in headers

    def test_empty_base_url_handled(self):
        config = ZephyrSquadConfig(
            auth_type=AUTH_TYPE_PAT,
            jira_base_url=None,
            pat_token="token",
        )
        client = ZephyrSquadPatClient(config)
        assert client.base_url == ""
