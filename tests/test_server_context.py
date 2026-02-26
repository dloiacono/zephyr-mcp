"""Tests for zephyr_mcp.server.context module."""

from zephyr_mcp.server.context import AppContext
from zephyr_mcp.squad.config import ZephyrSquadConfig
from zephyr_mcp.zephyr.config import ZephyrConfig


class TestAppContext:
    def test_default_values(self):
        ctx = AppContext()
        assert ctx.full_zephyr_config is None
        assert ctx.squad_config is None
        assert ctx.read_only is False
        assert ctx.enabled_tools is None

    def test_with_config(self):
        config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2")
        ctx = AppContext(full_zephyr_config=config, read_only=True)
        assert ctx.full_zephyr_config is config
        assert ctx.read_only is True

    def test_with_squad_config(self):
        squad_config = ZephyrSquadConfig(access_key="ak", secret_key="sk", account_id="aid")
        ctx = AppContext(squad_config=squad_config)
        assert ctx.squad_config is squad_config

    def test_with_both_configs(self):
        scale_config = ZephyrConfig(url="https://api.zephyrscale.smartbear.com/v2")
        squad_config = ZephyrSquadConfig(access_key="ak", secret_key="sk", account_id="aid")
        ctx = AppContext(full_zephyr_config=scale_config, squad_config=squad_config)
        assert ctx.full_zephyr_config is scale_config
        assert ctx.squad_config is squad_config

    def test_with_enabled_tools(self):
        ctx = AppContext(enabled_tools=["zephyr_get_test_case", "zephyr_search_test_cases"])
        assert ctx.enabled_tools == ["zephyr_get_test_case", "zephyr_search_test_cases"]
