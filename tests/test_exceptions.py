"""Tests for zephyr_mcp.exceptions module."""

from zephyr_mcp.exceptions import ZephyrAuthenticationError


class TestZephyrAuthenticationError:
    def test_is_exception(self):
        err = ZephyrAuthenticationError("auth failed")
        assert isinstance(err, Exception)

    def test_message(self):
        err = ZephyrAuthenticationError("auth failed 401")
        assert str(err) == "auth failed 401"

    def test_raise_and_catch(self):
        try:
            raise ZephyrAuthenticationError("test")
        except ZephyrAuthenticationError as e:
            assert str(e) == "test"
