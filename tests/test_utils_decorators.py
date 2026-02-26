"""Tests for zephyr_mcp.utils.decorators module."""

from unittest.mock import MagicMock

import pytest

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.utils.decorators import check_write_access


def _make_ctx(read_only: bool = False):
    """Create a mock FastMCP Context."""
    ctx = MagicMock()
    app_context = AppContext(full_zephyr_config=None, read_only=read_only)
    ctx.request_context.lifespan_context = {"app_lifespan_context": app_context}
    return ctx


class TestCheckWriteAccess:
    @pytest.mark.asyncio
    async def test_allows_write_when_not_read_only(self):
        @check_write_access
        async def my_tool(ctx):
            return "ok"

        ctx = _make_ctx(read_only=False)
        result = await my_tool(ctx)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_blocks_write_when_read_only(self):
        @check_write_access
        async def my_tool(ctx):
            return "ok"

        ctx = _make_ctx(read_only=True)
        with pytest.raises(ValueError, match="read-only mode"):
            await my_tool(ctx)

    @pytest.mark.asyncio
    async def test_allows_when_no_app_context(self):
        @check_write_access
        async def my_tool(ctx):
            return "ok"

        ctx = MagicMock()
        ctx.request_context.lifespan_context = {}
        result = await my_tool(ctx)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_allows_when_lifespan_not_dict(self):
        @check_write_access
        async def my_tool(ctx):
            return "ok"

        ctx = MagicMock()
        ctx.request_context.lifespan_context = None
        result = await my_tool(ctx)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        @check_write_access
        async def my_custom_tool(ctx):
            return "ok"

        assert my_custom_tool.__name__ == "my_custom_tool"

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self):
        @check_write_access
        async def my_tool(ctx, a, b, key=None):
            return f"{a}-{b}-{key}"

        ctx = _make_ctx(read_only=False)
        result = await my_tool(ctx, "x", "y", key="z")
        assert result == "x-y-z"
