"""Tests for zephyr_mcp.utils.oauth module."""

import json
import os
import time
from unittest.mock import MagicMock, patch

import pytest
import requests

from zephyr_mcp.utils.oauth import (
    BYOAccessTokenOAuthConfig,
    OAuthConfig,
    configure_oauth_session,
    get_oauth_config_from_env,
)


class TestOAuthConfig:
    def test_basic_creation(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="http://localhost/callback",
            scope="read write",
        )
        assert config.client_id == "id"
        assert config.client_secret == "secret"

    def test_cloud_id_and_base_url_cloud_url(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="http://localhost/callback",
            scope="read",
            cloud_id="cloud-123",
            base_url="https://mysite.atlassian.net",
        )
        assert config.base_url is None
        assert config.cloud_id == "cloud-123"

    def test_cloud_id_and_base_url_dc_raises(self):
        with pytest.raises(ValueError, match="cannot have both"):
            OAuthConfig(
                client_id="id",
                client_secret="secret",
                redirect_uri="http://localhost/callback",
                scope="read",
                cloud_id="cloud-123",
                base_url="https://jira.mycompany.com",
            )

    def test_is_data_center_false_no_base_url(self):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        assert config.is_data_center is False

    def test_is_data_center_true(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            base_url="https://jira.mycompany.com",
        )
        assert config.is_data_center is True

    def test_is_data_center_false_cloud_url(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            base_url="https://mysite.atlassian.net",
        )
        assert config.is_data_center is False

    def test_token_url_cloud(self):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        assert "auth.atlassian.com" in config.token_url

    def test_token_url_dc(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            base_url="https://jira.mycompany.com",
        )
        assert "jira.mycompany.com" in config.token_url

    def test_authorize_url_cloud(self):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        assert "auth.atlassian.com" in config.authorize_url

    def test_authorize_url_dc(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            base_url="https://jira.mycompany.com",
        )
        assert "jira.mycompany.com" in config.authorize_url

    def test_is_token_expired_no_token(self):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        assert config.is_token_expired is True

    def test_is_token_expired_no_expiry(self):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope", access_token="tok")
        assert config.is_token_expired is True

    def test_is_token_expired_false(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            access_token="tok",
            expires_at=time.time() + 3600,
        )
        assert config.is_token_expired is False

    def test_is_token_expired_true(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            access_token="tok",
            expires_at=time.time() - 100,
        )
        assert config.is_token_expired is True

    def test_get_authorization_url_cloud(self):
        config = OAuthConfig(client_id="myid", client_secret="secret", redirect_uri="http://localhost/cb", scope="read")
        url = config.get_authorization_url("state123")
        assert "client_id=myid" in url
        assert "state=state123" in url
        assert "audience=api.atlassian.com" in url

    def test_get_authorization_url_dc(self):
        config = OAuthConfig(
            client_id="myid",
            client_secret="secret",
            redirect_uri="http://localhost/cb",
            scope="WRITE",
            base_url="https://jira.mycompany.com",
        )
        url = config.get_authorization_url("state123")
        assert "audience" not in url
        assert "jira.mycompany.com" in url

    def test_get_keyring_username_cloud(self):
        config = OAuthConfig(client_id="myid", client_secret="secret", redirect_uri="uri", scope="scope", cloud_id="cloud-abc")
        assert "cloud-abc" in config._get_keyring_username()

    def test_get_keyring_username_dc(self):
        config = OAuthConfig(
            client_id="myid",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            base_url="https://jira.mycompany.com",
        )
        username = config._get_keyring_username()
        assert "dc-" in username

    def test_get_keyring_username_basic(self):
        config = OAuthConfig(client_id="myid", client_secret="secret", redirect_uri="uri", scope="scope")
        assert config._get_keyring_username() == "oauth-myid"

    @patch("zephyr_mcp.utils.oauth.requests.post")
    @patch.object(OAuthConfig, "_save_tokens")
    def test_exchange_code_success(self, mock_save, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.exchange_code_for_tokens("auth_code")
        assert result is True
        assert config.access_token == "new_access"
        assert config.refresh_token == "new_refresh"

    @patch("zephyr_mcp.utils.oauth.requests.post")
    def test_exchange_code_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.exchange_code_for_tokens("bad_code")
        assert result is False

    @patch("zephyr_mcp.utils.oauth.requests.post")
    def test_exchange_code_no_access_token(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"refresh_token": "ref"}
        mock_post.return_value = mock_response

        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.exchange_code_for_tokens("code")
        assert result is False

    @patch("zephyr_mcp.utils.oauth.requests.post")
    def test_exchange_code_no_refresh_cloud(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"access_token": "tok"}
        mock_post.return_value = mock_response

        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.exchange_code_for_tokens("code")
        assert result is False

    @patch("zephyr_mcp.utils.oauth.requests.post")
    @patch.object(OAuthConfig, "_save_tokens")
    def test_exchange_code_no_refresh_dc(self, mock_save, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"access_token": "tok", "expires_in": 3600}
        mock_post.return_value = mock_response

        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="WRITE",
            base_url="https://jira.mycompany.com",
        )
        result = config.exchange_code_for_tokens("code")
        assert result is True

    @patch("zephyr_mcp.utils.oauth.requests.post", side_effect=requests.exceptions.ConnectionError("fail"))
    def test_exchange_code_network_error(self, mock_post):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.exchange_code_for_tokens("code")
        assert result is False

    @patch("zephyr_mcp.utils.oauth.requests.post")
    @patch.object(OAuthConfig, "_save_tokens")
    def test_refresh_access_token_success(self, mock_save, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "refreshed", "expires_in": 3600}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope", refresh_token="old_refresh")
        result = config.refresh_access_token()
        assert result is True
        assert config.access_token == "refreshed"

    def test_refresh_access_token_no_refresh_token(self):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.refresh_access_token()
        assert result is False

    def test_ensure_valid_token_not_expired(self):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            access_token="tok",
            expires_at=time.time() + 3600,
        )
        assert config.ensure_valid_token() is True

    @patch.object(OAuthConfig, "refresh_access_token", return_value=True)
    def test_ensure_valid_token_expired_refreshes(self, mock_refresh):
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            access_token="tok",
            expires_at=time.time() - 100,
            refresh_token="ref",
        )
        assert config.ensure_valid_token() is True
        mock_refresh.assert_called_once()

    @patch("zephyr_mcp.utils.oauth.keyring")
    def test_load_tokens_from_keyring(self, mock_keyring):
        token_data = {"access_token": "tok", "refresh_token": "ref"}
        mock_keyring.get_password.return_value = json.dumps(token_data)
        result = OAuthConfig.load_tokens("myid")
        assert result == token_data

    @patch("zephyr_mcp.utils.oauth.keyring")
    def test_load_tokens_keyring_none(self, mock_keyring):
        mock_keyring.get_password.return_value = None
        with patch.object(OAuthConfig, "_load_tokens_from_file", return_value={}):
            result = OAuthConfig.load_tokens("myid")
            assert result == {}

    @patch("zephyr_mcp.utils.oauth.keyring")
    def test_load_tokens_keyring_error(self, mock_keyring):
        mock_keyring.get_password.side_effect = Exception("keyring error")
        with patch.object(OAuthConfig, "_load_tokens_from_file", return_value={"access_token": "file_tok"}):
            result = OAuthConfig.load_tokens("myid")
            assert result == {"access_token": "file_tok"}

    def test_from_env_no_vars(self):
        with patch.dict(os.environ, {}, clear=True):
            result = OAuthConfig.from_env()
            assert result is None

    @patch.object(OAuthConfig, "load_tokens", return_value={})
    def test_from_env_full_config(self, mock_load):
        env = {
            "ATLASSIAN_OAUTH_CLIENT_ID": "cid",
            "ATLASSIAN_OAUTH_CLIENT_SECRET": "csecret",
            "ATLASSIAN_OAUTH_REDIRECT_URI": "http://localhost/cb",
            "ATLASSIAN_OAUTH_SCOPE": "read write",
        }
        with patch.dict(os.environ, env, clear=True):
            result = OAuthConfig.from_env()
            assert result is not None
            assert result.client_id == "cid"

    def test_from_env_oauth_enabled_minimal(self):
        env = {"ATLASSIAN_OAUTH_ENABLE": "true"}
        with patch.dict(os.environ, env, clear=True):
            result = OAuthConfig.from_env()
            assert result is not None
            assert result.client_id == ""

    @patch.object(OAuthConfig, "load_tokens", return_value={})
    def test_from_env_dc_defaults(self, mock_load):
        env = {
            "ATLASSIAN_OAUTH_CLIENT_ID": "cid",
            "ATLASSIAN_OAUTH_CLIENT_SECRET": "csecret",
        }
        with patch.dict(os.environ, env, clear=True):
            result = OAuthConfig.from_env(service_url="https://jira.mycompany.com")
            assert result is not None
            assert result.redirect_uri == "http://localhost:8080/callback"
            assert result.scope == "WRITE"

    @patch("zephyr_mcp.utils.oauth.requests.post")
    def test_exchange_code_json_decode_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.side_effect = json.JSONDecodeError("err", "doc", 0)
        mock_response.text = "not json"
        mock_post.return_value = mock_response

        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.exchange_code_for_tokens("code")
        assert result is False

    @patch("zephyr_mcp.utils.oauth.requests.post")
    def test_exchange_code_generic_exception(self, mock_post):
        mock_post.side_effect = Exception("unexpected")
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = config.exchange_code_for_tokens("code")
        assert result is False

    @patch("zephyr_mcp.utils.oauth.requests.post")
    @patch.object(OAuthConfig, "_save_tokens")
    def test_refresh_access_token_updates_refresh_token(self, mock_save, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_in": 7200,
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        config = OAuthConfig(
            client_id="id", client_secret="secret", redirect_uri="uri", scope="scope",
            refresh_token="old_refresh",
        )
        result = config.refresh_access_token()
        assert result is True
        assert config.refresh_token == "new_refresh"
        mock_save.assert_called_once()

    @patch("zephyr_mcp.utils.oauth.requests.post")
    def test_refresh_access_token_failure(self, mock_post):
        mock_post.side_effect = Exception("network error")
        config = OAuthConfig(
            client_id="id", client_secret="secret", redirect_uri="uri", scope="scope",
            refresh_token="ref",
        )
        result = config.refresh_access_token()
        assert result is False

    @patch("zephyr_mcp.utils.oauth.requests.get")
    def test_get_cloud_id_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "cloud-xyz"}]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        config = OAuthConfig(
            client_id="id", client_secret="secret", redirect_uri="uri", scope="scope",
            access_token="tok",
        )
        config._get_cloud_id()
        assert config.cloud_id == "cloud-xyz"

    def test_get_cloud_id_skips_dc(self):
        config = OAuthConfig(
            client_id="id", client_secret="secret", redirect_uri="uri", scope="scope",
            base_url="https://jira.mycompany.com",
        )
        config._get_cloud_id()
        assert config.cloud_id is None

    def test_get_cloud_id_no_access_token(self):
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        config._get_cloud_id()
        assert config.cloud_id is None

    @patch("zephyr_mcp.utils.oauth.requests.get")
    def test_get_cloud_id_error(self, mock_get):
        mock_get.side_effect = Exception("fail")
        config = OAuthConfig(
            client_id="id", client_secret="secret", redirect_uri="uri", scope="scope",
            access_token="tok",
        )
        config._get_cloud_id()
        assert config.cloud_id is None

    @patch("zephyr_mcp.utils.oauth.keyring")
    @patch.object(OAuthConfig, "_save_tokens_to_file")
    def test_save_tokens_keyring_success(self, mock_file_save, mock_keyring):
        config = OAuthConfig(
            client_id="myid", client_secret="secret", redirect_uri="uri", scope="scope",
            access_token="tok", refresh_token="ref", cloud_id="cloud-1",
        )
        config._save_tokens()
        assert mock_keyring.set_password.call_count >= 1
        mock_file_save.assert_called_once()

    @patch("zephyr_mcp.utils.oauth.keyring")
    @patch.object(OAuthConfig, "_save_tokens_to_file")
    def test_save_tokens_keyring_error_falls_back_to_file(self, mock_file_save, mock_keyring):
        mock_keyring.set_password.side_effect = Exception("keyring unavailable")
        config = OAuthConfig(
            client_id="myid", client_secret="secret", redirect_uri="uri", scope="scope",
            access_token="tok", refresh_token="ref",
        )
        config._save_tokens()
        mock_file_save.assert_called()

    @patch("builtins.open", create=True)
    @patch("zephyr_mcp.utils.oauth.Path")
    def test_save_tokens_to_file_with_data(self, mock_path_cls, mock_open):
        mock_dir = MagicMock()
        mock_path_cls.home.return_value.__truediv__ = MagicMock(return_value=mock_dir)
        mock_dir.__truediv__ = MagicMock(return_value=MagicMock())

        config = OAuthConfig(
            client_id="myid", client_secret="secret", redirect_uri="uri", scope="scope",
            access_token="tok", refresh_token="ref",
        )
        config._save_tokens_to_file({"access_token": "tok"})

    @patch("builtins.open", side_effect=OSError("disk full"))
    @patch("zephyr_mcp.utils.oauth.Path")
    def test_save_tokens_to_file_error(self, mock_path_cls, mock_open):
        mock_dir = MagicMock()
        mock_path_cls.home.return_value.__truediv__ = MagicMock(return_value=mock_dir)
        mock_dir.__truediv__ = MagicMock(return_value=MagicMock())

        config = OAuthConfig(
            client_id="myid", client_secret="secret", redirect_uri="uri", scope="scope",
        )
        config._save_tokens_to_file(None)

    @patch("zephyr_mcp.utils.oauth.Path")
    def test_load_tokens_from_file_not_found(self, mock_path_cls):
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path_cls.home.return_value.__truediv__.return_value.__truediv__.return_value = mock_path
        result = OAuthConfig._load_tokens_from_file("myid")
        assert result == {}

    @patch("builtins.open")
    @patch("zephyr_mcp.utils.oauth.Path")
    def test_load_tokens_from_file_success(self, mock_path_cls, mock_open):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path_cls.home.return_value.__truediv__.return_value.__truediv__.return_value = mock_path
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({"access_token": "file_tok"})
        with patch("json.load", return_value={"access_token": "file_tok"}):
            result = OAuthConfig._load_tokens_from_file("myid")
            assert result == {"access_token": "file_tok"}

    @patch("builtins.open", side_effect=OSError("read error"))
    @patch("zephyr_mcp.utils.oauth.Path")
    def test_load_tokens_from_file_error(self, mock_path_cls, mock_open):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path_cls.home.return_value.__truediv__.return_value.__truediv__.return_value = mock_path
        result = OAuthConfig._load_tokens_from_file("myid")
        assert result == {}

    @patch.object(OAuthConfig, "load_tokens", return_value={})
    def test_from_env_cloud_missing_redirect_and_scope(self, mock_load):
        env = {
            "ATLASSIAN_OAUTH_CLIENT_ID": "cid",
            "ATLASSIAN_OAUTH_CLIENT_SECRET": "csecret",
        }
        with patch.dict(os.environ, env, clear=True):
            result = OAuthConfig.from_env()
            assert result is None

    @patch.object(OAuthConfig, "load_tokens")
    def test_from_env_restores_tokens(self, mock_load):
        mock_load.return_value = {
            "access_token": "saved_tok",
            "refresh_token": "saved_ref",
            "expires_at": 9999999999.0,
            "cloud_id": "restored-cloud",
            "base_url": None,
        }
        env = {
            "ATLASSIAN_OAUTH_CLIENT_ID": "cid",
            "ATLASSIAN_OAUTH_CLIENT_SECRET": "csecret",
            "ATLASSIAN_OAUTH_REDIRECT_URI": "http://localhost/cb",
            "ATLASSIAN_OAUTH_SCOPE": "read",
        }
        with patch.dict(os.environ, env, clear=True):
            result = OAuthConfig.from_env()
            assert result is not None
            assert result.access_token == "saved_tok"
            assert result.refresh_token == "saved_ref"
            assert result.cloud_id == "restored-cloud"


class TestBYOAccessTokenOAuthConfig:
    def test_basic_creation(self):
        config = BYOAccessTokenOAuthConfig(access_token="my-token")
        assert config.access_token == "my-token"
        assert config.refresh_token is None
        assert config.expires_at is None

    def test_is_data_center_false_no_url(self):
        config = BYOAccessTokenOAuthConfig(access_token="tok")
        assert config.is_data_center is False

    def test_is_data_center_true(self):
        config = BYOAccessTokenOAuthConfig(access_token="tok", base_url="https://jira.mycompany.com")
        assert config.is_data_center is True

    def test_is_data_center_false_cloud(self):
        config = BYOAccessTokenOAuthConfig(access_token="tok", base_url="https://mysite.atlassian.net")
        assert config.is_data_center is False

    def test_from_env_no_token(self):
        with patch.dict(os.environ, {}, clear=True):
            result = BYOAccessTokenOAuthConfig.from_env()
            assert result is None

    def test_from_env_token_no_cloud_id_no_url(self):
        with patch.dict(os.environ, {"ATLASSIAN_OAUTH_ACCESS_TOKEN": "tok"}, clear=True):
            result = BYOAccessTokenOAuthConfig.from_env()
            assert result is None

    def test_from_env_with_cloud_id(self):
        env = {"ATLASSIAN_OAUTH_ACCESS_TOKEN": "tok", "ATLASSIAN_OAUTH_CLOUD_ID": "cloud-123"}
        with patch.dict(os.environ, env, clear=True):
            result = BYOAccessTokenOAuthConfig.from_env()
            assert result is not None
            assert result.access_token == "tok"
            assert result.cloud_id == "cloud-123"

    def test_from_env_dc(self):
        env = {"ATLASSIAN_OAUTH_ACCESS_TOKEN": "tok"}
        with patch.dict(os.environ, env, clear=True):
            result = BYOAccessTokenOAuthConfig.from_env(service_url="https://jira.mycompany.com")
            assert result is not None
            assert result.base_url == "https://jira.mycompany.com"
            assert result.cloud_id is None


class TestGetOAuthConfigFromEnv:
    def test_returns_none_no_config(self):
        with patch.dict(os.environ, {}, clear=True):
            result = get_oauth_config_from_env()
            assert result is None

    def test_returns_byo_when_available(self):
        env = {"ATLASSIAN_OAUTH_ACCESS_TOKEN": "tok", "ATLASSIAN_OAUTH_CLOUD_ID": "cloud-123"}
        with patch.dict(os.environ, env, clear=True):
            result = get_oauth_config_from_env()
            assert isinstance(result, BYOAccessTokenOAuthConfig)

    @patch.object(OAuthConfig, "load_tokens", return_value={})
    def test_returns_oauth_when_no_byo(self, mock_load):
        env = {
            "ATLASSIAN_OAUTH_CLIENT_ID": "cid",
            "ATLASSIAN_OAUTH_CLIENT_SECRET": "csecret",
            "ATLASSIAN_OAUTH_REDIRECT_URI": "http://localhost/cb",
            "ATLASSIAN_OAUTH_SCOPE": "read",
        }
        with patch.dict(os.environ, env, clear=True):
            result = get_oauth_config_from_env()
            assert isinstance(result, OAuthConfig)


class TestConfigureOAuthSession:
    def test_no_tokens(self):
        session = requests.Session()
        config = OAuthConfig(client_id="id", client_secret="secret", redirect_uri="uri", scope="scope")
        result = configure_oauth_session(session, config)
        assert result is False

    def test_access_token_only(self):
        session = requests.Session()
        config = BYOAccessTokenOAuthConfig(access_token="my-token")
        result = configure_oauth_session(session, config)
        assert result is True
        assert session.headers["Authorization"] == "Bearer my-token"

    def test_byo_empty_token_with_refresh(self):
        session = requests.Session()
        config = BYOAccessTokenOAuthConfig(access_token="")
        # BYO has refresh_token=None always, so empty access_token + no refresh = no tokens
        result = configure_oauth_session(session, config)
        assert result is False

    @patch.object(OAuthConfig, "ensure_valid_token", return_value=True)
    def test_full_oauth_valid_token(self, mock_ensure):
        session = requests.Session()
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            access_token="valid_tok",
            refresh_token="ref_tok",
        )
        result = configure_oauth_session(session, config)
        assert result is True
        assert "Bearer" in session.headers["Authorization"]

    @patch.object(OAuthConfig, "ensure_valid_token", return_value=False)
    def test_full_oauth_invalid_token(self, mock_ensure):
        session = requests.Session()
        config = OAuthConfig(
            client_id="id",
            client_secret="secret",
            redirect_uri="uri",
            scope="scope",
            access_token="expired_tok",
            refresh_token="ref_tok",
        )
        result = configure_oauth_session(session, config)
        assert result is False
