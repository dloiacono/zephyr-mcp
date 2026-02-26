"""Tests for zephyr_mcp.server.tools error branches not covered in main test file."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.tools import (
    zephyr_create_test_case,
    zephyr_create_test_cycle,
    zephyr_create_test_execution,
    zephyr_get_test_cycle,
    zephyr_get_test_execution,
    zephyr_link_test_case_to_issue,
    zephyr_search_test_cases,
    zephyr_update_test_case,
    zephyr_update_test_execution,
)


def _make_ctx(read_only=False):
    ctx = MagicMock()
    app_context = AppContext(full_zephyr_config=None, read_only=read_only)
    ctx.request_context.lifespan_context = {"app_lifespan_context": app_context}
    return ctx


class TestGenericErrorBranches:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_search_test_cases_generic_error(self, mock_get_fetcher):
        fetcher = MagicMock()
        fetcher.search_test_cases.side_effect = Exception("timeout")
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_search_test_cases(ctx, "PROJ")
        assert "Error searching test cases" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_create_test_case_generic_error(self, mock_get_fetcher):
        fetcher = MagicMock()
        fetcher.create_test_case.side_effect = Exception("server error")
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_create_test_case(ctx, "PROJ", "Test")
        assert "Error creating test case" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_update_test_case_generic_error(self, mock_get_fetcher):
        fetcher = MagicMock()
        fetcher.update_test_case.side_effect = Exception("server error")
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_update_test_case(ctx, "PROJ-T1", name="Updated")
        assert "Error updating test case" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_get_test_cycle_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("timeout")
        ctx = _make_ctx()

        result = await zephyr_get_test_cycle(ctx, "PROJ-R1")
        assert "Error getting test cycle" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_create_test_cycle_generic_error(self, mock_get_fetcher):
        fetcher = MagicMock()
        fetcher.create_test_cycle.side_effect = Exception("server error")
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_create_test_cycle(ctx, "PROJ", "Cycle")
        assert "Error creating test cycle" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_get_test_execution_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("timeout")
        ctx = _make_ctx()

        result = await zephyr_get_test_execution(ctx, "12345")
        assert "Error getting test execution" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_create_test_execution_generic_error(self, mock_get_fetcher):
        fetcher = MagicMock()
        fetcher.create_test_execution.side_effect = Exception("server error")
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_create_test_execution(ctx, "PROJ", "PROJ-T1", "PROJ-R1")
        assert "Error creating test execution" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_update_test_execution_generic_error(self, mock_get_fetcher):
        fetcher = MagicMock()
        fetcher.update_test_execution.side_effect = Exception("server error")
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_update_test_execution(ctx, "12345", status_name="Pass")
        assert "Error updating test execution" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_link_test_case_generic_error(self, mock_get_fetcher):
        fetcher = MagicMock()
        fetcher.link_test_case_to_issue.side_effect = Exception("server error")
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_link_test_case_to_issue(ctx, "PROJ-T1", "PROJ-123")
        assert "Error linking test case" in result
