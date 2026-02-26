"""Tests for zephyr_mcp.server.dependencies HTTP request context branches."""

from unittest.mock import MagicMock, patch

import pytest

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.server.dependencies import _create_user_config, _get_app_context, get_zephyr_fetcher
from zephyr_mcp.zephyr import ZephyrFetcher
from zephyr_mcp.zephyr.config import ZephyrConfig


def _make_ctx(config=None, read_only=False):
    ctx = MagicMock()
    app_context = AppContext(full_zephyr_config=config, read_only=read_only)
    ctx.request_context.lifespan_context = {"app_lifespan_context": app_context}
    return ctx


class TestGetAppContext:
    def test_returns_app_context_from_dict(self):
        ctx = MagicMock()
        app_ctx = AppContext(full_zephyr_config=None, read_only=True)
        ctx.request_context.lifespan_context = {"app_lifespan_context": app_ctx}
        result = _get_app_context(ctx)
        assert result is app_ctx
        assert result.read_only is True

    def test_returns_none_when_not_dict(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = "not a dict"
        result = _get_app_context(ctx)
        assert result is None

    def test_returns_none_when_key_missing(self):
        ctx = MagicMock()
        ctx.request_context.lifespan_context = {}
        result = _get_app_context(ctx)
        assert result is None


class TestCreateUserConfig:
    def test_pat_auth(self):
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="old-token",
        )
        result = _create_user_config(base_config, auth_type="pat", token="new-token")
        assert result.auth_type == "pat"
        assert result.personal_token == "new-token"
        assert result.oauth_config is None
        assert result.email is None
        assert result.api_token is None
        assert result.url == base_config.url

    def test_oauth_auth(self):
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="old-token",
        )
        result = _create_user_config(base_config, auth_type="oauth", token="oauth-access-token")
        assert result.auth_type == "oauth"
        assert result.oauth_config is not None
        assert result.oauth_config.access_token == "oauth-access-token"
        assert result.personal_token is None
        assert result.email is None
        assert result.api_token is None

    def test_unsupported_auth_type_raises(self):
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="tok",
        )
        with pytest.raises(ValueError, match="Unsupported auth_type"):
            _create_user_config(base_config, auth_type="basic", token="tok")


class TestGetZephyrFetcherHttpContext:
    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_returns_cached_fetcher_from_request_state(self, mock_fetcher_cls, mock_get_request):
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = MagicMock(spec=ZephyrFetcher)
        mock_get_request.return_value = mock_request

        ctx = _make_ctx()
        result = await get_zephyr_fetcher(ctx)
        assert result is mock_request.state.zephyr_fetcher
        mock_fetcher_cls.assert_not_called()

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_header_based_pat_auth(self, mock_fetcher_cls, mock_get_request):
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = None
        mock_request.state.user_auth_type = "pat"
        mock_request.state.service_headers = {
            "X-Zephyr-Url": "https://api.zephyrscale.smartbear.com/v2",
            "X-Zephyr-Personal-Token": "header-token",
        }
        del mock_request.state.user_token  # no user_token attribute
        mock_get_request.return_value = mock_request

        mock_fetcher = MagicMock(spec=ZephyrFetcher)
        mock_fetcher_cls.return_value = mock_fetcher

        ctx = _make_ctx()
        result = await get_zephyr_fetcher(ctx)
        assert result is mock_fetcher
        mock_fetcher_cls.assert_called_once()
        call_kwargs = mock_fetcher_cls.call_args
        config_arg = call_kwargs[1]["config"]
        assert config_arg.url == "https://api.zephyrscale.smartbear.com/v2"
        assert config_arg.auth_type == "pat"
        assert config_arg.personal_token == "header-token"

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_header_based_creation_failure(self, mock_fetcher_cls, mock_get_request):
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = None
        mock_request.state.user_auth_type = "pat"
        mock_request.state.service_headers = {
            "X-Zephyr-Url": "https://api.zephyrscale.smartbear.com/v2",
            "X-Zephyr-Personal-Token": "bad-token",
        }
        del mock_request.state.user_token
        mock_get_request.return_value = mock_request
        mock_fetcher_cls.side_effect = Exception("connection refused")

        ctx = _make_ctx()
        with pytest.raises(ValueError, match="Invalid header-based"):
            await get_zephyr_fetcher(ctx)

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_user_token_pat_auth(self, mock_fetcher_cls, mock_get_request):
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="global-token",
        )
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = None
        mock_request.state.user_auth_type = "pat"
        mock_request.state.user_token = "user-specific-token"
        mock_request.state.service_headers = {}
        mock_get_request.return_value = mock_request

        mock_fetcher = MagicMock(spec=ZephyrFetcher)
        mock_fetcher_cls.return_value = mock_fetcher

        ctx = _make_ctx(config=base_config)
        result = await get_zephyr_fetcher(ctx)
        assert result is mock_fetcher

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_user_token_empty_raises(self, mock_fetcher_cls, mock_get_request):
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="global-token",
        )
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = None
        mock_request.state.user_auth_type = "pat"
        mock_request.state.user_token = ""
        mock_request.state.service_headers = {}
        mock_get_request.return_value = mock_request

        ctx = _make_ctx(config=base_config)
        with pytest.raises(ValueError, match="empty"):
            await get_zephyr_fetcher(ctx)

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_user_token_no_global_config_raises(self, mock_fetcher_cls, mock_get_request):
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = None
        mock_request.state.user_auth_type = "pat"
        mock_request.state.user_token = "user-token"
        mock_request.state.service_headers = {}
        mock_get_request.return_value = mock_request

        ctx = _make_ctx(config=None)
        with pytest.raises(ValueError, match="not available"):
            await get_zephyr_fetcher(ctx)

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_user_token_creation_failure(self, mock_fetcher_cls, mock_get_request):
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="global-token",
        )
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = None
        mock_request.state.user_auth_type = "pat"
        mock_request.state.user_token = "bad-user-token"
        mock_request.state.service_headers = {}
        mock_get_request.return_value = mock_request
        mock_fetcher_cls.side_effect = Exception("auth failed")

        ctx = _make_ctx(config=base_config)
        with pytest.raises(ValueError, match="Invalid user"):
            await get_zephyr_fetcher(ctx)

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    @patch("zephyr_mcp.server.dependencies.ZephyrFetcher")
    async def test_no_user_auth_falls_back_to_global(self, mock_fetcher_cls, mock_get_request):
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="global-token",
        )
        mock_request = MagicMock()
        mock_request.state.zephyr_fetcher = None
        mock_request.state.user_auth_type = None
        mock_request.state.service_headers = {}
        mock_get_request.return_value = mock_request

        mock_fetcher = MagicMock(spec=ZephyrFetcher)
        mock_fetcher_cls.return_value = mock_fetcher

        ctx = _make_ctx(config=base_config)
        result = await get_zephyr_fetcher(ctx)
        assert result is mock_fetcher

    @pytest.mark.asyncio
    @patch("fastmcp.server.dependencies.get_http_request")
    async def test_runtime_error_falls_back_to_global(self, mock_get_request):
        mock_get_request.side_effect = RuntimeError("Not in HTTP context")
        base_config = ZephyrConfig(
            url="https://api.zephyrscale.smartbear.com/v2",
            auth_type="pat",
            personal_token="global-token",
        )
        ctx = _make_ctx(config=base_config)

        with patch("zephyr_mcp.server.dependencies.ZephyrFetcher") as mock_fetcher_cls:
            mock_fetcher = MagicMock(spec=ZephyrFetcher)
            mock_fetcher_cls.return_value = mock_fetcher
            result = await get_zephyr_fetcher(ctx)
            assert result is mock_fetcher
