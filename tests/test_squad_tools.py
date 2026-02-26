"""Tests for zephyr_mcp.server.squad_tools module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zephyr_mcp.exceptions import ZephyrAuthenticationError
from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.squad_tools import (
    _format_result,
    squad_add_test_to_cycle,
    squad_create_cycle,
    squad_get_cycle,
    squad_get_cycles,
    squad_get_execution,
    squad_get_executions_by_cycle,
    squad_update_execution,
    squad_zql_search,
)


def _make_ctx(read_only=False):
    ctx = MagicMock()
    app_context = AppContext(full_zephyr_config=None, squad_config=None, read_only=read_only)
    ctx.request_context.lifespan_context = {"app_lifespan_context": app_context}
    return ctx


def _make_fetcher():
    fetcher = MagicMock()
    fetcher.get_cycle.return_value = {"id": "1", "name": "Cycle 1"}
    fetcher.get_cycles.return_value = [{"id": "1"}, {"id": "2"}]
    fetcher.create_cycle.return_value = {"id": "new-cycle"}
    fetcher.get_execution.return_value = {"id": "100", "status": {"id": 1}}
    fetcher.get_executions_by_cycle.return_value = {"executions": []}
    fetcher.add_test_to_cycle.return_value = {"id": "200"}
    fetcher.update_execution.return_value = {"id": "100", "status": {"id": 2}}
    fetcher.get_zql_search.return_value = {"executions": [], "totalCount": 0}
    return fetcher


class TestFormatResult:
    def test_dict_result(self):
        result = _format_result("Test", {"key": "val"})
        assert "## Test" in result
        assert '"key"' in result

    def test_list_result(self):
        result = _format_result("Test", [{"key": "val"}])
        assert "## Test" in result

    def test_string_result(self):
        result = _format_result("Test", "simple string")
        assert "## Test" in result
        assert "simple string" in result


class TestSquadGetCycle:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await squad_get_cycle(ctx, "1", "10200")
        assert "Cycle 1" in result
        fetcher.get_cycle.assert_called_once_with("1", "10200", "-1")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("401")
        ctx = _make_ctx()

        result = await squad_get_cycle(ctx, "1", "10200")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("connection failed")
        ctx = _make_ctx()

        result = await squad_get_cycle(ctx, "1", "10200")
        assert "Error" in result


class TestSquadGetCycles:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await squad_get_cycles(ctx, "10200")
        assert "Squad Test Cycles" in result
        fetcher.get_cycles.assert_called_once_with("10200", "-1")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx()

        result = await squad_get_cycles(ctx, "10200")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("fail")
        ctx = _make_ctx()

        result = await squad_get_cycles(ctx, "10200")
        assert "Error" in result


class TestSquadCreateCycle:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await squad_create_cycle(ctx, "10200", "Sprint 1")
        assert "new-cycle" in result

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await squad_create_cycle(ctx, "10200", "Sprint 1")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx(read_only=False)

        result = await squad_create_cycle(ctx, "10200", "Cycle")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("fail")
        ctx = _make_ctx(read_only=False)

        result = await squad_create_cycle(ctx, "10200", "Cycle")
        assert "Error" in result


class TestSquadGetExecution:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await squad_get_execution(ctx, "100")
        assert "100" in result
        fetcher.get_execution.assert_called_once_with("100")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx()

        result = await squad_get_execution(ctx, "100")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("fail")
        ctx = _make_ctx()

        result = await squad_get_execution(ctx, "100")
        assert "Error" in result


class TestSquadGetExecutionsByCycle:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await squad_get_executions_by_cycle(ctx, "10200", "5")
        assert "Squad Test Executions" in result
        fetcher.get_executions_by_cycle.assert_called_once_with("10200", "5", "-1")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx()

        result = await squad_get_executions_by_cycle(ctx, "10200", "5")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("fail")
        ctx = _make_ctx()

        result = await squad_get_executions_by_cycle(ctx, "10200", "5")
        assert "Error" in result


class TestSquadAddTestToCycle:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await squad_add_test_to_cycle(ctx, "5", "10200", "99999")
        assert "200" in result
        fetcher.add_test_to_cycle.assert_called_once_with("5", "10200", "99999", "-1")

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await squad_add_test_to_cycle(ctx, "5", "10200", "99999")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx(read_only=False)

        result = await squad_add_test_to_cycle(ctx, "5", "10200", "99999")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("fail")
        ctx = _make_ctx(read_only=False)

        result = await squad_add_test_to_cycle(ctx, "5", "10200", "99999")
        assert "Error" in result


class TestSquadUpdateExecution:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx(read_only=False)

        result = await squad_update_execution(ctx, "100", status="PASS")
        assert "100" in result

    @pytest.mark.asyncio
    async def test_blocked_read_only(self):
        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only"):
            await squad_update_execution(ctx, "100", status="PASS")

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_invalid_status(self, mock_get_fetcher):
        ctx = _make_ctx(read_only=False)
        result = await squad_update_execution(ctx, "100", status="INVALID")
        assert "Invalid status" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx(read_only=False)

        result = await squad_update_execution(ctx, "100")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("fail")
        ctx = _make_ctx(read_only=False)

        result = await squad_update_execution(ctx, "100")
        assert "Error" in result


class TestSquadZqlSearch:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_success(self, mock_get_fetcher):
        fetcher = _make_fetcher()
        mock_get_fetcher.return_value = fetcher
        ctx = _make_ctx()

        result = await squad_zql_search(ctx, 'project = "PROJ"')
        assert "Squad ZQL Search Results" in result
        fetcher.get_zql_search.assert_called_once_with('project = "PROJ"', 50, 0)

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_auth_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = ZephyrAuthenticationError("denied")
        ctx = _make_ctx()

        result = await squad_zql_search(ctx, "query")
        assert "Authentication error" in result

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_tools.get_squad_fetcher", new_callable=AsyncMock)
    async def test_generic_error(self, mock_get_fetcher):
        mock_get_fetcher.side_effect = Exception("fail")
        ctx = _make_ctx()

        result = await squad_zql_search(ctx, "query")
        assert "Error" in result
