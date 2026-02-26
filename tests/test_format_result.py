"""Tests for _format_result helper in zephyr_mcp.server.tools."""

from zephyr_mcp.server.tools import _format_result


class TestFormatResult:
    def test_dict_result(self):
        result = _format_result("Title", {"key": "value"})
        assert "## Title" in result
        assert '"key": "value"' in result
        assert "```json" in result

    def test_list_result(self):
        result = _format_result("Title", [{"a": 1}, {"b": 2}])
        assert "## Title" in result
        assert "```json" in result

    def test_string_result(self):
        result = _format_result("Title", "plain text")
        assert "## Title" in result
        assert "plain text" in result
        assert "```json" not in result

    def test_int_result(self):
        result = _format_result("Title", 42)
        assert "## Title" in result
        assert "42" in result
