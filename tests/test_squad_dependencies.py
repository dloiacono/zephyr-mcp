"""Tests for zephyr_mcp.server.squad_dependencies module."""

from unittest.mock import MagicMock, patch

import pytest

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.squad_dependencies import get_squad_fetcher
from zephyr_mcp.squad import SquadFetcher
from zephyr_mcp.squad.config import ZephyrSquadConfig


def _make_squad_config():
    return ZephyrSquadConfig(
        base_url="https://prod-api.zephyr4jiracloud.com/connect",
        access_key="ak",
        secret_key="sk",
        account_id="aid",
    )


def _make_ctx(squad_config=None, zephyr_config=None, read_only=False):
    ctx = MagicMock()
    app_context = AppContext(full_zephyr_config=zephyr_config, squad_config=squad_config, read_only=read_only)
    ctx.request_context.lifespan_context = {"app_lifespan_context": app_context}
    return ctx


class TestGetSquadFetcher:
    @pytest.mark.asyncio
    async def test_returns_fetcher_from_lifespan_config(self):
        config = _make_squad_config()
        ctx = _make_ctx(squad_config=config)

        fetcher = await get_squad_fetcher(ctx)
        assert isinstance(fetcher, SquadFetcher)
        assert fetcher.config is config

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_dependencies.ZephyrSquadConfig.from_env")
    async def test_falls_back_to_env(self, mock_from_env):
        mock_from_env.return_value = _make_squad_config()
        ctx = _make_ctx(squad_config=None)

        fetcher = await get_squad_fetcher(ctx)
        assert isinstance(fetcher, SquadFetcher)
        mock_from_env.assert_called_once()

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.squad_dependencies.ZephyrSquadConfig.from_env")
    async def test_raises_when_no_config(self, mock_from_env):
        mock_from_env.side_effect = ValueError("missing env")
        ctx = _make_ctx(squad_config=None)

        with pytest.raises(ValueError, match="Zephyr Squad client not available"):
            await get_squad_fetcher(ctx)

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_lifespan(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {}

        with pytest.raises(ValueError):
            await get_squad_fetcher(ctx)

    @pytest.mark.asyncio
    async def test_returns_none_for_non_dict_lifespan(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = "not-a-dict"

        with pytest.raises(ValueError):
            await get_squad_fetcher(ctx)
