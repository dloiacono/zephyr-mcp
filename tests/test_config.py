"""Tests for zephyr_mcp.zephyr.config module."""

import os
from unittest.mock import patch

import pytest

from zephyr_mcp.zephyr.config import ZephyrConfig


class TestZephyrConfig:
    def test_default_values(self):
        config = ZephyrConfig()
        assert config.url is None
        assert config.auth_type == "pat"
        assert config.ssl_verify is True
        assert config.custom_headers is None

    def test_is_cloud_true(self):
        config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2")
        assert config.is_cloud is True

    def test_is_cloud_false(self):
        config = ZephyrConfig(url="https://jira.mycompany.com/zephyr")
        assert config.is_cloud is False

    def test_is_cloud_none_url(self):
        config = ZephyrConfig(url=None)
        assert config.is_cloud is False


class TestZephyrConfigFromEnv:
    def test_no_url_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ZEPHYR_URL"):
                ZephyrConfig.from_env()

    def test_no_auth_raises(self):
        with patch.dict(os.environ, {"ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2"}, clear=True):
            with pytest.raises(ValueError, match="authentication"):
                ZephyrConfig.from_env()

    def test_pat_auth(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_PERSONAL_TOKEN": "my-token-123",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.auth_type == "pat"
            assert config.personal_token == "my-token-123"
            assert config.url == "https://api.zephyrscale.smartbear.com/v2"

    def test_basic_auth(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_EMAIL": "user@example.com",
            "ZEPHYR_API_TOKEN": "api-token-456",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.auth_type == "basic"
            assert config.email == "user@example.com"
            assert config.api_token == "api-token-456"

    def test_pat_takes_precedence(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_PERSONAL_TOKEN": "my-token",
            "ZEPHYR_EMAIL": "user@example.com",
            "ZEPHYR_API_TOKEN": "api-token",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.auth_type == "pat"

    def test_project_key(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_PERSONAL_TOKEN": "tok",
            "ZEPHYR_PROJECT_KEY": "PROJ",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.project_key == "PROJ"

    def test_ssl_verify_false(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_PERSONAL_TOKEN": "tok",
            "ZEPHYR_SSL_VERIFY": "false",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.ssl_verify is False

    def test_proxy_settings(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_PERSONAL_TOKEN": "tok",
            "ZEPHYR_HTTP_PROXY": "http://proxy:8080",
            "ZEPHYR_HTTPS_PROXY": "https://proxy:8443",
            "ZEPHYR_NO_PROXY": "localhost",
            "ZEPHYR_SOCKS_PROXY": "socks5://proxy:1080",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.http_proxy == "http://proxy:8080"
            assert config.https_proxy == "https://proxy:8443"
            assert config.no_proxy == "localhost"
            assert config.socks_proxy == "socks5://proxy:1080"

    def test_fallback_proxy_env_vars(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_PERSONAL_TOKEN": "tok",
            "HTTP_PROXY": "http://fallback:8080",
            "HTTPS_PROXY": "https://fallback:8443",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.http_proxy == "http://fallback:8080"
            assert config.https_proxy == "https://fallback:8443"

    def test_custom_headers(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ZEPHYR_PERSONAL_TOKEN": "tok",
            "ZEPHYR_CUSTOM_HEADERS": "X-Custom=val1,X-Other=val2",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.custom_headers == {"X-Custom": "val1", "X-Other": "val2"}

    def test_oauth_auth_from_env(self):
        env = {
            "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
            "ATLASSIAN_OAUTH_ACCESS_TOKEN": "oauth-tok",
            "ATLASSIAN_OAUTH_CLOUD_ID": "cloud-123",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ZephyrConfig.from_env()
            assert config.auth_type == "bearer"
            assert config.personal_token == "oauth-tok"
