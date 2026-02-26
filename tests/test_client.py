"""Tests for zephyr_mcp.zephyr.client module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.zephyr.client import ZephyrClient
from zephyr_mcp.zephyr.config import ZephyrConfig


def _make_config(**overrides) -> ZephyrConfig:
    defaults = {
        "url": "https://api.zephyrscale.smartbear.com/v2",
        "auth_type": "pat",
        "personal_token": "test-token-123",
        "ssl_verify": True,
    }
    defaults.update(overrides)
    return ZephyrConfig(**defaults)


class TestZephyrClientInit:
    def test_pat_auth(self):
        config = _make_config()
        client = ZephyrClient(config)
        assert "Bearer" in client.session.headers.get("Authorization", "")
        assert client.base_url == "https://api.zephyrscale.smartbear.com/v2"

    def test_basic_auth(self):
        config = _make_config(auth_type="basic", personal_token=None, email="user@example.com", api_token="api-tok")
        client = ZephyrClient(config)
        assert "Basic" in client.session.headers.get("Authorization", "")

    def test_bearer_auth(self):
        config = _make_config(auth_type="bearer")
        client = ZephyrClient(config)
        assert "Bearer" in client.session.headers.get("Authorization", "")

    def test_invalid_auth_raises(self):
        config = _make_config(auth_type="invalid", personal_token=None)
        with pytest.raises(ZephyrAuthenticationError):
            ZephyrClient(config)

    def test_oauth_auth(self):
        mock_oauth = MagicMock()
        mock_oauth.access_token = "oauth-access-tok"
        mock_oauth.refresh_token = None

        with patch("zephyr_mcp.zephyr.client.configure_oauth_session", return_value=True):
            config = _make_config(auth_type="oauth", personal_token=None, oauth_config=mock_oauth)
            client = ZephyrClient(config)
            assert client is not None

    def test_oauth_auth_failure_raises(self):
        mock_oauth = MagicMock()

        with patch("zephyr_mcp.zephyr.client.configure_oauth_session", return_value=False):
            config = _make_config(auth_type="oauth", personal_token=None, oauth_config=mock_oauth)
            with pytest.raises(ZephyrAuthenticationError):
                ZephyrClient(config)

    def test_custom_headers(self):
        config = _make_config(custom_headers={"X-Custom": "value"})
        client = ZephyrClient(config)
        assert client.session.headers.get("X-Custom") == "value"

    def test_strips_trailing_slash(self):
        config = _make_config(url="https://api.example.com/v2/")
        client = ZephyrClient(config)
        assert client.base_url == "https://api.example.com/v2"


class TestZephyrClientProxies:
    def test_http_proxy(self):
        config = _make_config(http_proxy="http://proxy:8080")
        client = ZephyrClient(config)
        assert client.session.proxies.get("http") == "http://proxy:8080"

    def test_https_proxy(self):
        config = _make_config(https_proxy="https://proxy:8443")
        client = ZephyrClient(config)
        assert client.session.proxies.get("https") == "https://proxy:8443"

    def test_socks_proxy_overrides(self):
        config = _make_config(socks_proxy="socks5://proxy:1080", http_proxy="http://proxy:8080")
        client = ZephyrClient(config)
        assert client.session.proxies.get("http") == "socks5://proxy:1080"
        assert client.session.proxies.get("https") == "socks5://proxy:1080"


class TestZephyrClientRequest:
    def _make_client(self):
        config = _make_config()
        return ZephyrClient(config)

    @patch.object(requests.Session, "request")
    def test_get(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "T123"}
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        client = self._make_client()
        result = client.get("/testcases/T123")
        assert result == {"key": "T123"}
        mock_request.assert_called_once()

    @patch.object(requests.Session, "request")
    def test_post(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "T124"}
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        client = self._make_client()
        result = client.post("/testcases", json={"name": "Test"})
        assert result == {"key": "T124"}

    @patch.object(requests.Session, "request")
    def test_put(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "T123", "name": "Updated"}
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        client = self._make_client()
        result = client.put("/testcases/T123", json={"name": "Updated"})
        assert result == {"key": "T123", "name": "Updated"}

    @patch.object(requests.Session, "request")
    def test_delete(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        client = self._make_client()
        result = client.delete("/testcases/T123")
        assert result == {}

    @patch.object(requests.Session, "request")
    def test_auth_error_401(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_request.return_value = mock_response

        client = self._make_client()
        with pytest.raises(ZephyrAuthenticationError, match="401"):
            client.get("/testcases/T123")

    @patch.object(requests.Session, "request")
    def test_auth_error_403(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_request.return_value = mock_response

        client = self._make_client()
        with pytest.raises(ZephyrAuthenticationError, match="403"):
            client.get("/testcases/T123")

    @patch.object(requests.Session, "request")
    def test_http_error_raises(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_request.return_value = mock_response

        client = self._make_client()
        with pytest.raises(requests.exceptions.HTTPError):
            client.get("/testcases/T123")

    @patch.object(requests.Session, "request")
    def test_request_builds_url(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response

        client = self._make_client()
        client.get("/testcases/T123")

        call_args = mock_request.call_args
        assert call_args[0][1] == "https://api.zephyrscale.smartbear.com/v2/testcases/T123"
