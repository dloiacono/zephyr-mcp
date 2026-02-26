"""Tests for zephyr_mcp.squad.config module."""

import os
from unittest.mock import patch

import pytest

from zephyr_mcp.squad.config import AUTH_TYPE_JWT, AUTH_TYPE_PAT, SQUAD_BASE_URL, ZephyrSquadConfig


class TestZephyrSquadConfig:
    def test_default_values(self):
        config = ZephyrSquadConfig()
        assert config.auth_type == AUTH_TYPE_JWT
        assert config.base_url == SQUAD_BASE_URL
        assert config.access_key is None
        assert config.secret_key is None
        assert config.account_id is None
        assert config.project_id is None
        assert config.jira_base_url is None
        assert config.pat_token is None
        assert config.jira_email is None

    def test_custom_jwt_values(self):
        config = ZephyrSquadConfig(
            auth_type=AUTH_TYPE_JWT,
            base_url="https://custom.example.com",
            access_key="ak",
            secret_key="sk",
            account_id="aid",
            project_id="pid",
        )
        assert config.auth_type == AUTH_TYPE_JWT
        assert config.base_url == "https://custom.example.com"
        assert config.access_key == "ak"
        assert config.secret_key == "sk"
        assert config.account_id == "aid"
        assert config.project_id == "pid"

    def test_custom_pat_values(self):
        config = ZephyrSquadConfig(
            auth_type=AUTH_TYPE_PAT,
            jira_base_url="https://jira.example.com",
            pat_token="my-pat-token",
            jira_email="user@example.com",
            project_id="10200",
        )
        assert config.auth_type == AUTH_TYPE_PAT
        assert config.jira_base_url == "https://jira.example.com"
        assert config.pat_token == "my-pat-token"
        assert config.jira_email == "user@example.com"
        assert config.project_id == "10200"


class TestFromEnvJwt:
    @patch.dict(
        os.environ,
        {
            "ZEPHYR_SQUAD_ACCESS_KEY": "test-access-key",
            "ZEPHYR_SQUAD_SECRET_KEY": "test-secret-key",
            "ZEPHYR_SQUAD_ACCOUNT_ID": "test-account-id",
        },
        clear=True,
    )
    def test_minimal_jwt_config(self):
        config = ZephyrSquadConfig.from_env()
        assert config.auth_type == AUTH_TYPE_JWT
        assert config.access_key == "test-access-key"
        assert config.secret_key == "test-secret-key"
        assert config.account_id == "test-account-id"
        assert config.base_url == SQUAD_BASE_URL
        assert config.project_id is None

    @patch.dict(
        os.environ,
        {
            "ZEPHYR_SQUAD_ACCESS_KEY": "ak",
            "ZEPHYR_SQUAD_SECRET_KEY": "sk",
            "ZEPHYR_SQUAD_ACCOUNT_ID": "aid",
            "ZEPHYR_SQUAD_PROJECT_ID": "10200",
            "ZEPHYR_SQUAD_BASE_URL": "https://custom.example.com",
        },
        clear=True,
    )
    def test_full_jwt_config(self):
        config = ZephyrSquadConfig.from_env()
        assert config.auth_type == AUTH_TYPE_JWT
        assert config.access_key == "ak"
        assert config.secret_key == "sk"
        assert config.account_id == "aid"
        assert config.project_id == "10200"
        assert config.base_url == "https://custom.example.com"

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_all_raises(self):
        with pytest.raises(ValueError, match="ZEPHYR_SQUAD_PAT_TOKEN.*ZEPHYR_SQUAD_ACCESS_KEY"):
            ZephyrSquadConfig.from_env()

    @patch.dict(os.environ, {"ZEPHYR_SQUAD_ACCESS_KEY": "ak"}, clear=True)
    def test_missing_secret_key_raises(self):
        with pytest.raises(ValueError, match="ZEPHYR_SQUAD_SECRET_KEY"):
            ZephyrSquadConfig.from_env()

    @patch.dict(
        os.environ,
        {"ZEPHYR_SQUAD_ACCESS_KEY": "ak", "ZEPHYR_SQUAD_SECRET_KEY": "sk"},
        clear=True,
    )
    def test_missing_account_id_raises(self):
        with pytest.raises(ValueError, match="ZEPHYR_SQUAD_ACCOUNT_ID"):
            ZephyrSquadConfig.from_env()


class TestFromEnvPat:
    @patch.dict(
        os.environ,
        {
            "ZEPHYR_SQUAD_PAT_TOKEN": "my-pat-token",
            "ZEPHYR_SQUAD_JIRA_BASE_URL": "https://jira.example.com",
        },
        clear=True,
    )
    def test_minimal_pat_config(self):
        config = ZephyrSquadConfig.from_env()
        assert config.auth_type == AUTH_TYPE_PAT
        assert config.pat_token == "my-pat-token"
        assert config.jira_base_url == "https://jira.example.com"
        assert config.jira_email is None

    @patch.dict(
        os.environ,
        {
            "ZEPHYR_SQUAD_PAT_TOKEN": "my-pat-token",
            "ZEPHYR_SQUAD_JIRA_BASE_URL": "https://jira.example.com/",
            "ZEPHYR_SQUAD_JIRA_EMAIL": "user@example.com",
            "ZEPHYR_SQUAD_PROJECT_ID": "10200",
        },
        clear=True,
    )
    def test_full_pat_config(self):
        config = ZephyrSquadConfig.from_env()
        assert config.auth_type == AUTH_TYPE_PAT
        assert config.pat_token == "my-pat-token"
        assert config.jira_base_url == "https://jira.example.com"
        assert config.jira_email == "user@example.com"
        assert config.project_id == "10200"

    @patch.dict(
        os.environ,
        {"ZEPHYR_SQUAD_PAT_TOKEN": "my-pat-token"},
        clear=True,
    )
    def test_missing_jira_base_url_raises(self):
        with pytest.raises(ValueError, match="ZEPHYR_SQUAD_JIRA_BASE_URL"):
            ZephyrSquadConfig.from_env()

    @patch.dict(
        os.environ,
        {
            "ZEPHYR_SQUAD_PAT_TOKEN": "my-pat-token",
            "ZEPHYR_SQUAD_JIRA_BASE_URL": "https://jira.example.com",
            "ZEPHYR_SQUAD_ACCESS_KEY": "ak",
            "ZEPHYR_SQUAD_SECRET_KEY": "sk",
            "ZEPHYR_SQUAD_ACCOUNT_ID": "aid",
        },
        clear=True,
    )
    def test_pat_takes_precedence_over_jwt(self):
        config = ZephyrSquadConfig.from_env()
        assert config.auth_type == AUTH_TYPE_PAT
