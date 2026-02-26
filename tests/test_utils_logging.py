"""Tests for zephyr_mcp.utils.logging module."""

import logging

from zephyr_mcp.utils.logging import get_masked_session_headers, mask_sensitive, setup_logging


class TestSetupLogging:
    def test_default_level(self):
        logger = setup_logging()
        assert logger.name == "mcp-zephyr"

    def test_custom_level(self):
        setup_logging(level=logging.DEBUG)
        root = logging.getLogger()
        assert root.level == logging.DEBUG

    def test_returns_logger(self):
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)


class TestMaskSensitive:
    def test_none_value(self):
        assert mask_sensitive(None) == "Not Provided"

    def test_empty_string(self):
        assert mask_sensitive("") == "Not Provided"

    def test_short_string(self):
        result = mask_sensitive("abcd")
        assert result == "****"

    def test_exact_boundary(self):
        result = mask_sensitive("abcdefgh")
        assert result == "********"

    def test_long_string(self):
        result = mask_sensitive("abcdefghijklmnop")
        assert result.startswith("abcd")
        assert result.endswith("mnop")
        assert "****" in result

    def test_custom_keep_chars(self):
        result = mask_sensitive("abcdefghijklmnop", keep_chars=2)
        assert result.startswith("ab")
        assert result.endswith("op")

    def test_preserves_length(self):
        value = "mysecrettoken12345"
        result = mask_sensitive(value)
        assert len(result) == len(value)


class TestGetMaskedSessionHeaders:
    def test_non_sensitive_headers(self):
        headers = {"Content-Type": "application/json", "Accept": "text/html"}
        masked = get_masked_session_headers(headers)
        assert masked["Content-Type"] == "application/json"
        assert masked["Accept"] == "text/html"

    def test_basic_auth_header(self):
        headers = {"Authorization": "Basic dXNlcjpwYXNzd29yZA=="}
        masked = get_masked_session_headers(headers)
        assert masked["Authorization"].startswith("Basic ")
        assert "dXNlcjpwYXNzd29yZA==" not in masked["Authorization"]

    def test_bearer_auth_header(self):
        headers = {"Authorization": "Bearer my-secret-token-12345"}
        masked = get_masked_session_headers(headers)
        assert masked["Authorization"].startswith("Bearer ")
        assert "my-secret-token-12345" not in masked["Authorization"]

    def test_other_auth_header(self):
        headers = {"Authorization": "CustomScheme mysecret"}
        masked = get_masked_session_headers(headers)
        assert "mysecret" not in masked["Authorization"]

    def test_cookie_header(self):
        headers = {"Cookie": "session=abc123secret"}
        masked = get_masked_session_headers(headers)
        assert "abc123secret" not in masked["Cookie"]

    def test_mixed_headers(self):
        headers = {
            "Authorization": "Bearer token123456789",
            "Content-Type": "application/json",
            "Cookie": "session=secret",
        }
        masked = get_masked_session_headers(headers)
        assert masked["Content-Type"] == "application/json"
        assert "token123456789" not in masked["Authorization"]
        assert "secret" not in masked["Cookie"]
