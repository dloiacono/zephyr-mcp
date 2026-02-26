"""Tests for zephyr_mcp.zephyr ZephyrFetcher class."""

from unittest.mock import MagicMock, patch

from zephyr_mcp.zephyr import ZephyrFetcher
from zephyr_mcp.zephyr.config import ZephyrConfig
from zephyr_mcp.zephyr.testcases import TestCasesMixin
from zephyr_mcp.zephyr.testcycles import TestCyclesMixin
from zephyr_mcp.zephyr.testexecutions import TestExecutionsMixin


class TestZephyrFetcher:
    @patch("zephyr_mcp.zephyr.ZephyrClient")
    def test_inherits_all_mixins(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2", auth_type="pat", personal_token="tok")
        fetcher = ZephyrFetcher(config)

        assert isinstance(fetcher, TestCasesMixin)
        assert isinstance(fetcher, TestCyclesMixin)
        assert isinstance(fetcher, TestExecutionsMixin)

    @patch("zephyr_mcp.zephyr.ZephyrClient")
    def test_has_client(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2", auth_type="pat", personal_token="tok")
        fetcher = ZephyrFetcher(config)

        assert fetcher.client is not None
        mock_client_cls.assert_called_once_with(config)

    @patch("zephyr_mcp.zephyr.ZephyrClient")
    def test_has_test_case_methods(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2", auth_type="pat", personal_token="tok")
        fetcher = ZephyrFetcher(config)

        assert hasattr(fetcher, "get_test_case")
        assert hasattr(fetcher, "search_test_cases")
        assert hasattr(fetcher, "create_test_case")
        assert hasattr(fetcher, "update_test_case")
        assert hasattr(fetcher, "delete_test_case")
        assert hasattr(fetcher, "link_test_case_to_issue")

    @patch("zephyr_mcp.zephyr.ZephyrClient")
    def test_has_test_cycle_methods(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2", auth_type="pat", personal_token="tok")
        fetcher = ZephyrFetcher(config)

        assert hasattr(fetcher, "get_test_cycle")
        assert hasattr(fetcher, "search_test_cycles")
        assert hasattr(fetcher, "create_test_cycle")
        assert hasattr(fetcher, "update_test_cycle")
        assert hasattr(fetcher, "delete_test_cycle")
        assert hasattr(fetcher, "link_test_cycle_to_issue")

    @patch("zephyr_mcp.zephyr.ZephyrClient")
    def test_has_test_execution_methods(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2", auth_type="pat", personal_token="tok")
        fetcher = ZephyrFetcher(config)

        assert hasattr(fetcher, "get_test_execution")
        assert hasattr(fetcher, "search_test_executions")
        assert hasattr(fetcher, "create_test_execution")
        assert hasattr(fetcher, "update_test_execution")
        assert hasattr(fetcher, "delete_test_execution")
        assert hasattr(fetcher, "get_test_execution_results")
