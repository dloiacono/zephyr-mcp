"""Tests for zephyr_mcp.server.tools module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.tools import (
    _format_result,
    zephyr_create_test_case,
    zephyr_create_test_cycle,
    zephyr_create_test_execution,
    zephyr_get_test_case,
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


def _make_fetcher():
    fetcher = MagicMock()
    fetcher.get_test_case.return_value = {"key": "PROJ-T1", "name": "Test"}
    fetcher.search_test_cases.return_value = {"values": [{"key": "PROJ-T1"}], "total": 1}
    fetcher.create_test_case.return_value = {"key": "PROJ-T2"}
    fetcher.update_test_case.return_value = {"key": "PROJ-T1", "name": "Updated"}
    fetcher.get_test_cycle.return_value = {"key": "PROJ-R1", "name": "Cycle"}
    fetcher.create_test_cycle.return_value = {"key": "PROJ-R2"}
    fetcher.get_test_execution.return_value = {"id": "12345", "statusName": "Pass"}
    fetcher.create_test_execution.return_value = {"id": "12346"}
    fetcher.update_test_execution.return_value = {"id": "12345", "statusName": "Fail"}
    fetcher.link_test_case_to_issue.return_value = {}
    return fetcher


class TestFormatResult:
    def test_dict_result(self):
        result = _format_result("Test", {"key": "val"})
        assert "## Test" in result
        assert '"key"' in result

    def test_list_result(self):
        result = _format_result("Test", [{"key": "val"}])
        assert "## Test" in result
        assert '"key"' in result

    def test_string_result(self):
        result = _format_result("Test", "simple string")
        assert "## Test" in result
        assert "simple string" in result


class TestZephyrGetTestCase:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_get_test_case(ctx, "PROJ-T1")
        assert "PROJ-T1" in result
        fetcher.get_test_case.assert_called_once_with("PROJ-T1")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("401")
        ctx = _make_ctx()

        result = await zephyr_get_test_case(ctx, "PROJ-T1")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("connection failed")
        ctx = _make_ctx()

        result = await zephyr_get_test_case(ctx, "PROJ-T1")
        assert "Error" in result


class TestZephyrSearchTestCases:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_search_test_cases(ctx, "PROJ", query="login")
        assert "PROJ-T1" in result
        fetcher.search_test_cases.assert_called_once_with("PROJ", query="login", max_results=50, start_at=0)

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("forbidden")
        ctx = _make_ctx()

        result = await zephyr_search_test_cases(ctx, "PROJ")
        assert "Authentication error" in result


class TestZephyrCreateTestCase:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await zephyr_create_test_case(ctx, "PROJ", "New Test")
        assert "PROJ-T2" in result

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await zephyr_create_test_case(ctx, "PROJ", "New Test")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_invalid_status(self, mock_get_fetcher):
        ctx = _make_ctx(read_only=False)
        result = await zephyr_create_test_case(ctx, "PROJ", "Test", status="InvalidStatus")
        assert "Invalid status" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_invalid_priority(self, mock_get_fetcher):
        ctx = _make_ctx(read_only=False)
        result = await zephyr_create_test_case(ctx, "PROJ", "Test", priority="InvalidPriority")
        assert "Invalid priority" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx(read_only=False)

        result = await zephyr_create_test_case(ctx, "PROJ", "Test")
        assert "Authentication error" in result


class TestZephyrUpdateTestCase:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await zephyr_update_test_case(ctx, "PROJ-T1", name="Updated")
        assert "Updated" in result

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await zephyr_update_test_case(ctx, "PROJ-T1", name="Updated")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_invalid_status(self, mock_get_fetcher):
        ctx = _make_ctx(read_only=False)
        result = await zephyr_update_test_case(ctx, "PROJ-T1", status="Bad")
        assert "Invalid status" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_invalid_priority(self, mock_get_fetcher):
        ctx = _make_ctx(read_only=False)
        result = await zephyr_update_test_case(ctx, "PROJ-T1", priority="Bad")
        assert "Invalid priority" in result


class TestZephyrGetTestCycle:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_get_test_cycle(ctx, "PROJ-R1")
        assert "PROJ-R1" in result
        fetcher.get_test_cycle.assert_called_once_with("PROJ-R1")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx()

        result = await zephyr_get_test_cycle(ctx, "PROJ-R1")
        assert "Authentication error" in result


class TestZephyrCreateTestCycle:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await zephyr_create_test_cycle(ctx, "PROJ", "Sprint Cycle")
        assert "PROJ-R2" in result

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await zephyr_create_test_cycle(ctx, "PROJ", "Cycle")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx(read_only=False)

        result = await zephyr_create_test_cycle(ctx, "PROJ", "Cycle")
        assert "Authentication error" in result


class TestZephyrGetTestExecution:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await zephyr_get_test_execution(ctx, "12345")
        assert "12345" in result
        fetcher.get_test_execution.assert_called_once_with("12345")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx()

        result = await zephyr_get_test_execution(ctx, "12345")
        assert "Authentication error" in result


class TestZephyrCreateTestExecution:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await zephyr_create_test_execution(ctx, "PROJ", "PROJ-T1", "PROJ-R1", status_name="Pass")
        assert "12346" in result

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await zephyr_create_test_execution(ctx, "PROJ", "PROJ-T1", "PROJ-R1")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_invalid_status(self, mock_get_fetcher):
        ctx = _make_ctx(read_only=False)
        result = await zephyr_create_test_execution(ctx, "PROJ", "PROJ-T1", "PROJ-R1", status_name="BadStatus")
        assert "Invalid status" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx(read_only=False)

        result = await zephyr_create_test_execution(ctx, "PROJ", "PROJ-T1", "PROJ-R1")
        assert "Authentication error" in result


class TestZephyrUpdateTestExecution:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await zephyr_update_test_execution(ctx, "12345", status_name="Fail")
        assert "Fail" in result

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await zephyr_update_test_execution(ctx, "12345", status_name="Fail")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_invalid_status(self, mock_get_fetcher):
        ctx = _make_ctx(read_only=False)
        result = await zephyr_update_test_execution(ctx, "12345", status_name="BadStatus")
        assert "Invalid status" in result


class TestZephyrLinkTestCaseToIssue:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await zephyr_link_test_case_to_issue(ctx, "PROJ-T1", "PROJ-123")
        assert "Linked" in result
        fetcher.link_test_case_to_issue.assert_called_once_with("PROJ-T1", "PROJ-123")

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await zephyr_link_test_case_to_issue(ctx, "PROJ-T1", "PROJ-123")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.tools.get_zephyr_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx(read_only=False)

        result = await zephyr_link_test_case_to_issue(ctx, "PROJ-T1", "PROJ-123")
        assert "Authentication error" in result
