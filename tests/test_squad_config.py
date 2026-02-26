"""Tests for zephyr_mcp.squad.config module."""

import os
from unittest.mock import patch

import pytest

from zephyr_mcp.squad.config import SQUAD_BASE_URL, ZephyrSquadConfig


class TestZephyrSquadConfig:
    def test_default_values(self):
        config = ZephyrSquadConfig()
        assert config.base_url == SQUAD_BASE_URL
        assert config.access_key is None
        assert config.secret_key is None
        assert config.account_id is None
        assert config.project_id is None

    def test_custom_values(self):
        config = ZephyrSquadConfig(
            base_url="https://custom.example.com",
            access_key="ak",
            secret_key="sk",
            account_id="aid",
            project_id="pid",
        )
        assert config.base_url == "https://custom.example.com"
        assert config.access_key == "ak"
        assert config.secret_key == "sk"
        assert config.account_id == "aid"
        assert config.project_id == "pid"


class TestFromEnv:
    @patch.dict(
        os.environ,
        {
            "ZEPHYR_SQUAD_ACCESS_KEY": "test-access-key",
            "ZEPHYR_SQUAD_SECRET_KEY": "test-secret-key",
            "ZEPHYR_SQUAD_ACCOUNT_ID": "test-account-id",
        },
        clear=False,
    )
    def test_minimal_config(self):
        config = ZephyrSquadConfig.from_env()
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
        clear=False,
    )
    def test_full_config(self):
        config = ZephyrSquadConfig.from_env()
        assert config.access_key == "ak"
        assert config.secret_key == "sk"
        assert config.account_id == "aid"
        assert config.project_id == "10200"
        assert config.base_url == "https://custom.example.com"

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_access_key_raises(self):
        with pytest.raises(ValueError, match="ZEPHYR_SQUAD_ACCESS_KEY"):
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
