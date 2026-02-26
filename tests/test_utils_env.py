"""Tests for zephyr_mcp.utils.env module."""

import os
from unittest.mock import patch

from zephyr_mcp.utils.env import get_custom_headers, is_env_extended_truthy, is_env_ssl_verify, is_env_truthy


class TestIsEnvTruthy:
    def test_true_values(self):
        for val in ("true", "True", "TRUE", "1", "yes", "Yes", "YES"):
            with patch.dict(os.environ, {"TEST_VAR": val}):
                assert is_env_truthy("TEST_VAR") is True

    def test_false_values(self):
        for val in ("false", "0", "no", "random", ""):
            with patch.dict(os.environ, {"TEST_VAR": val}):
                assert is_env_truthy("TEST_VAR") is False

    def test_missing_var(self):
        with patch.dict(os.environ, {}, clear=True):
            assert is_env_truthy("NONEXISTENT_VAR") is False

    def test_default_value(self):
        with patch.dict(os.environ, {}, clear=True):
            assert is_env_truthy("NONEXISTENT_VAR", "true") is True


class TestIsEnvExtendedTruthy:
    def test_extended_true_values(self):
        for val in ("true", "1", "yes", "y", "on", "Y", "ON"):
            with patch.dict(os.environ, {"TEST_VAR": val}):
                assert is_env_extended_truthy("TEST_VAR") is True

    def test_false_values(self):
        for val in ("false", "0", "no", "off", ""):
            with patch.dict(os.environ, {"TEST_VAR": val}):
                assert is_env_extended_truthy("TEST_VAR") is False

    def test_missing_var(self):
        with patch.dict(os.environ, {}, clear=True):
            assert is_env_extended_truthy("NONEXISTENT_VAR") is False


class TestIsEnvSslVerify:
    def test_default_is_true(self):
        with patch.dict(os.environ, {}, clear=True):
            assert is_env_ssl_verify("ZEPHYR_SSL_VERIFY") is True

    def test_false_values(self):
        for val in ("false", "False", "FALSE", "0", "no", "No"):
            with patch.dict(os.environ, {"ZEPHYR_SSL_VERIFY": val}):
                assert is_env_ssl_verify("ZEPHYR_SSL_VERIFY") is False

    def test_true_values(self):
        for val in ("true", "True", "1", "yes"):
            with patch.dict(os.environ, {"ZEPHYR_SSL_VERIFY": val}):
                assert is_env_ssl_verify("ZEPHYR_SSL_VERIFY") is True


class TestGetCustomHeaders:
    def test_empty_env(self):
        with patch.dict(os.environ, {}, clear=True):
            assert get_custom_headers("ZEPHYR_CUSTOM_HEADERS") == {}

    def test_empty_string(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": ""}):
            assert get_custom_headers("ZEPHYR_CUSTOM_HEADERS") == {}

    def test_whitespace_string(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": "   "}):
            assert get_custom_headers("ZEPHYR_CUSTOM_HEADERS") == {}

    def test_single_header(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": "X-Custom=value1"}):
            result = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")
            assert result == {"X-Custom": "value1"}

    def test_multiple_headers(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": "X-Custom=value1,X-Other=value2"}):
            result = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")
            assert result == {"X-Custom": "value1", "X-Other": "value2"}

    def test_value_with_equals(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": "X-Custom=val=ue"}):
            result = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")
            assert result == {"X-Custom": "val=ue"}

    def test_strips_whitespace(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": " X-Custom = value1 , X-Other = value2 "}):
            result = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")
            assert result == {"X-Custom": "value1", "X-Other": "value2"}

    def test_skips_invalid_pairs(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": "X-Custom=value1,invalidpair,X-Other=value2"}):
            result = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")
            assert result == {"X-Custom": "value1", "X-Other": "value2"}

    def test_skips_empty_key(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": "=value1,X-Other=value2"}):
            result = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")
            assert result == {"X-Other": "value2"}

    def test_skips_empty_pairs(self):
        with patch.dict(os.environ, {"ZEPHYR_CUSTOM_HEADERS": "X-Custom=value1,,X-Other=value2"}):
            result = get_custom_headers("ZEPHYR_CUSTOM_HEADERS")
            assert result == {"X-Custom": "value1", "X-Other": "value2"}
