"""Tests for zephyr_mcp.server.factory module."""

from unittest.mock import patch

import pytest
from fastmcp import FastMCP

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.factory import create_server
from zephyr_mcp.zephyr.config import ZephyrConfig


class TestCreateServer:
    def test_returns_fastmcp_instance(self):
        server = create_server(read_only=False)
        assert server is not None
        assert isinstance(server, FastMCP)
        assert server.name == "Zephyr Scale MCP"

    def test_read_only_flag(self):
        server = create_server(read_only=True)
        assert server is not None
        assert isinstance(server, FastMCP)

    def test_default_not_read_only(self):
        server = create_server()
        assert server is not None
        assert isinstance(server, FastMCP)


class TestLifespan:
    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.factory.ZephyrConfig.from_env")
    async def test_lifespan_loads_config(self, mock_from_env):
        """Test lifespan yields AppContext with loaded config."""
        fake_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="test-token",
        )
        mock_from_env.return_value = fake_config

        server = create_server(read_only=False)
        async with server._lifespan_manager():
            result = server._lifespan_result
            assert result is not None
            assert "app_lifespan_context" in result
            app_ctx = result["app_lifespan_context"]
            assert isinstance(app_ctx, AppContext)
            assert app_ctx.full_zephyr_config is fake_config
            assert app_ctx.read_only is False

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.factory.ZephyrConfig.from_env")
    async def test_lifespan_config_failure_continues(self, mock_from_env):
        """Test lifespan handles config load failure gracefully."""
        mock_from_env.side_effect = Exception("No env vars set")

        server = create_server(read_only=True)
        async with server._lifespan_manager():
            result = server._lifespan_result
            app_ctx = result["app_lifespan_context"]
            assert app_ctx.full_zephyr_config is None
            assert app_ctx.read_only is True

    @pytest.mark.asyncio
    @patch("zephyr_mcp.server.factory.ZephyrConfig.from_env")
    async def test_lifespan_read_only_propagated(self, mock_from_env):
        """Test read_only flag is passed through to AppContext."""
        mock_from_env.return_value = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="tok",
        )
        server = create_server(read_only=True)
        async with server._lifespan_manager():
            result = server._lifespan_result
            assert result["app_lifespan_context"].read_only is True
