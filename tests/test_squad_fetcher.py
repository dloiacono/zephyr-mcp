"""Tests for zephyr_mcp.squad SquadFetcher module."""

from unittest.mock import patch

from zephyr_mcp.squad import SquadFetcher, _create_squad_client
from zephyr_mcp.squad.client import ZephyrSquadClient
from zephyr_mcp.squad.config import AUTH_TYPE_JWT, AUTH_TYPE_PAT, ZephyrSquadConfig
from zephyr_mcp.squad.pat_client import ZephyrSquadPatClient


def _make_jwt_config():
    return ZephyrSquadConfig(
        auth_type=AUTH_TYPE_JWT,
        base_url="https://prod-api.zephyr4jiracloud.com/connect",
        access_key="ak",
        secret_key="sk",
        account_id="aid",
    )


def _make_pat_config():
    return ZephyrSquadConfig(
        auth_type=AUTH_TYPE_PAT,
        jira_base_url="https://jira.example.com",
        pat_token="my-pat-token",
    )


class TestCreateSquadClient:
    def test_creates_jwt_client_for_jwt_config(self):
        client = _create_squad_client(_make_jwt_config())
        assert isinstance(client, ZephyrSquadClient)

    def test_creates_pat_client_for_pat_config(self):
        client = _create_squad_client(_make_pat_config())
        assert isinstance(client, ZephyrSquadPatClient)


class TestSquadFetcher:
    def test_init_with_jwt_config(self):
        config = _make_jwt_config()
        fetcher = SquadFetcher(config=config)
        assert fetcher.config is config
        assert isinstance(fetcher.client, ZephyrSquadClient)

    def test_init_with_pat_config(self):
        config = _make_pat_config()
        fetcher = SquadFetcher(config=config)
        assert fetcher.config is config
        assert isinstance(fetcher.client, ZephyrSquadPatClient)

    @patch("zephyr_mcp.squad.ZephyrSquadConfig.from_env")
    def test_init_from_env(self, mock_from_env):
        mock_from_env.return_value = _make_jwt_config()
        fetcher = SquadFetcher()
        assert fetcher.config is not None
        mock_from_env.assert_called_once()

    def test_has_cycle_methods(self):
        fetcher = SquadFetcher(config=_make_jwt_config())
        assert hasattr(fetcher, "get_cycle")
        assert hasattr(fetcher, "get_cycles")
        assert hasattr(fetcher, "create_cycle")
        assert hasattr(fetcher, "update_cycle")
        assert hasattr(fetcher, "delete_cycle")

    def test_has_execution_methods(self):
        fetcher = SquadFetcher(config=_make_jwt_config())
        assert hasattr(fetcher, "get_execution")
        assert hasattr(fetcher, "get_executions_by_cycle")
        assert hasattr(fetcher, "add_test_to_cycle")
        assert hasattr(fetcher, "update_execution")
        assert hasattr(fetcher, "get_zql_search")
