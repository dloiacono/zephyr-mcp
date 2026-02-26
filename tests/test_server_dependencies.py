"""Tests for zephyr_mcp.server.dependencies module."""

from unittest.mock import MagicMock, patch

import pytest

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.dependencies import get_zephyr_fetcher
from zephyr_mcp.zephyr import ZephyrFetcher
from zephyr_mcp.zephyr.config import ZephyrConfig


def _make_ctx(config=None, read_only=False):
    ctx = MagicMock()
    app_context = AppContext(full_zephyr_config=config, read_only=read_only)
    ctx.request_context.lifespan_context = {"app_lifespan_context": app_context}
    return ctx


class TestGetZephyrFetcher:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_returns_fetcher_with_config(self, mock_fetcher_cls):
        config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="tok",
        )
        ctx = _make_ctx(config=config)
        mock_fetcher_cls.return_value = MagicMock(spec=ZephyrFetcher)

        result = await get_zephyr_fetcher(ctx)
        mock_fetcher_cls.assert_called_once_with(config=config)
        assert result is not None

    @pytest.mark.asyncio
    async def test_no_config_raises(self):
        ctx = _make_ctx(config=None)
        with pytest.raises(ValueError, match="not available"):
            await get_zephyr_fetcher(ctx)

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_global_config_fallback(self, mock_fetcher_cls):
        config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="tok",
        )
        ctx = _make_ctx(config=config)
        mock_fetcher_cls.return_value = MagicMock(spec=ZephyrFetcher)

        result = await get_zephyr_fetcher(ctx)
        assert result is not None
