"""Tests for zephyr_mcp.squad SquadFetcher module."""

from unittest.mock import patch

import pytest

from zephyr_mcp.squad import SquadFetcher
from zephyr_mcp.squad.config import ZephyrSquadConfig


def _make_config():
    return ZephyrSquadConfig(
        base_url="https://prod-api.zephyr4jiracloud.com/connect",
        access_key="ak",
        secret_key="sk",
        account_id="aid",
    )


class TestSquadFetcher:
    def test_init_with_config(self):
        config = _make_config()
        fetcher = SquadFetcher(config=config)
        assert fetcher.config is config
        assert fetcher.client is not None

    @patch("zephyr_mcp.squad.ZephyrSquadConfig.from_env")
    def test_init_from_env(self, mock_from_env):
        mock_from_env.return_value = _make_config()
        fetcher = SquadFetcher()
        assert fetcher.config is not None
        mock_from_env.assert_called_once()

    def test_has_cycle_methods(self):
        fetcher = SquadFetcher(config=_make_config())
        assert hasattr(fetcher, "get_cycle")
        assert hasattr(fetcher, "get_cycles")
        assert hasattr(fetcher, "create_cycle")
        assert hasattr(fetcher, "update_cycle")
        assert hasattr(fetcher, "delete_cycle")

    def test_has_execution_methods(self):
        fetcher = SquadFetcher(config=_make_config())
        assert hasattr(fetcher, "get_execution")
        assert hasattr(fetcher, "get_executions_by_cycle")
        assert hasattr(fetcher, "add_test_to_cycle")
        assert hasattr(fetcher, "update_execution")
        assert hasattr(fetcher, "get_zql_search")
