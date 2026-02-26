"""Tests for zephyr_mcp.squad.jwt_auth module."""

import hashlib
import time
from unittest.mock import patch

import jwt

from zephyr_mcp.squad.jwt_auth import JWT_EXPIRY_SECONDS, _build_canonical_path, generate_jwt_token


class TestBuildCanonicalPath:
    def test_get_no_params(self):
        result = _build_canonical_path("GET", "/public/rest/api/1.0/cycle")
        assert result == "GET&/public/rest/api/1.0/cycle&"

    def test_post_no_params(self):
        result = _build_canonical_path("post", "/public/rest/api/1.0/cycle")
        assert result == "POST&/public/rest/api/1.0/cycle&"

    def test_get_with_params(self):
        result = _build_canonical_path("GET", "/public/rest/api/1.0/cycle", {"projectId": "10200", "versionId": "-1"})
        assert result == "GET&/public/rest/api/1.0/cycle&projectId=10200&versionId=-1"

    def test_params_sorted(self):
        result = _build_canonical_path("GET", "/path", {"z": "1", "a": "2", "m": "3"})
        assert result == "GET&/path&a=2&m=3&z=1"

    def test_empty_params(self):
        result = _build_canonical_path("DELETE", "/path", {})
        assert result == "DELETE&/path&"

    def test_none_params(self):
        result = _build_canonical_path("PUT", "/path", None)
        assert result == "PUT&/path&"


class TestGenerateJwtToken:
    def test_token_structure(self):
        token = generate_jwt_token(
            access_key="test-access",
            secret_key="test-secret",
            account_id="test-account",
            http_method="GET",
            relative_path="/public/rest/api/1.0/cycle",
        )
        assert isinstance(token, str)
        assert len(token) > 0

        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert decoded["sub"] == "test-account"
        assert decoded["iss"] == "test-access"
        assert "qsh" in decoded
        assert "iat" in decoded
        assert "exp" in decoded

    def test_qsh_matches_canonical(self):
        token = generate_jwt_token(
            access_key="ak",
            secret_key="sk",
            account_id="aid",
            http_method="POST",
            relative_path="/public/rest/api/1.0/cycle",
        )
        decoded = jwt.decode(token, "sk", algorithms=["HS256"])

        expected_canonical = "POST&/public/rest/api/1.0/cycle&"
        expected_qsh = hashlib.sha256(expected_canonical.encode("utf-8")).hexdigest()
        assert decoded["qsh"] == expected_qsh

    def test_qsh_with_query_params(self):
        token = generate_jwt_token(
            access_key="ak",
            secret_key="sk",
            account_id="aid",
            http_method="GET",
            relative_path="/path",
            query_params={"projectId": "10200"},
        )
        decoded = jwt.decode(token, "sk", algorithms=["HS256"])

        expected_canonical = "GET&/path&projectId=10200"
        expected_qsh = hashlib.sha256(expected_canonical.encode("utf-8")).hexdigest()
        assert decoded["qsh"] == expected_qsh

    @patch("zephyr_mcp.squad.jwt_auth.time")
    def test_expiry(self, mock_time):
        mock_time.time.return_value = 1000000
        token = generate_jwt_token(
            access_key="ak",
            secret_key="sk",
            account_id="aid",
            http_method="GET",
            relative_path="/path",
        )
        decoded = jwt.decode(token, "sk", algorithms=["HS256"], options={"verify_exp": False})
        assert decoded["iat"] == 1000000
        assert decoded["exp"] == 1000000 + JWT_EXPIRY_SECONDS

    def test_different_methods_produce_different_tokens(self):
        args = dict(access_key="ak", secret_key="sk", account_id="aid", relative_path="/path")
        token_get = generate_jwt_token(http_method="GET", **args)
        token_post = generate_jwt_token(http_method="POST", **args)
        assert token_get != token_post
