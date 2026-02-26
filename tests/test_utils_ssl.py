"""Tests for zephyr_mcp.utils.ssl module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from zephyr_mcp.utils.ssl import SSLIgnoreAdapter, configure_ssl_verification


class TestSSLIgnoreAdapter:
    def test_init_poolmanager_creates_context(self):
        adapter = SSLIgnoreAdapter()
        adapter.init_poolmanager(1, 1)
        assert adapter.poolmanager is not None

    def test_cert_verify_disables_verification(self):
        adapter = SSLIgnoreAdapter()
        conn = MagicMock()
        with patch.object(requests.adapters.HTTPAdapter, "cert_verify") as mock_parent:
            adapter.cert_verify(conn, "https://example.com", True, None)
            mock_parent.assert_called_once_with(conn, "https://example.com", verify=False, cert=None)


class TestConfigureSslVerification:
    def test_ssl_verify_true_no_certs(self):
        session = requests.Session()
        configure_ssl_verification("Zephyr", "https://example.com", session, ssl_verify=True)
        # No adapter should be mounted for SSL ignore
        assert not any(isinstance(v, SSLIgnoreAdapter) for v in session.adapters.values())

    def test_ssl_verify_false_mounts_adapter(self):
        session = requests.Session()
        configure_ssl_verification("Zephyr", "https://example.com", session, ssl_verify=False)
        assert any(isinstance(v, SSLIgnoreAdapter) for v in session.adapters.values())

    def test_client_cert_configured(self):
        session = requests.Session()
        configure_ssl_verification(
            "Zephyr",
            "https://example.com",
            session,
            ssl_verify=True,
            client_cert="/path/to/cert.pem",
            client_key="/path/to/key.pem",
        )
        assert session.cert == ("/path/to/cert.pem", "/path/to/key.pem")

    def test_client_cert_with_password_raises(self):
        session = requests.Session()
        try:
            configure_ssl_verification(
                "Zephyr",
                "https://example.com",
                session,
                ssl_verify=True,
                client_cert="/path/to/cert.pem",
                client_key="/path/to/key.pem",
                client_key_password="secret",
            )
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "encrypted" in str(e).lower() or "private key" in str(e).lower()

    def test_ssl_false_with_custom_domain(self):
        session = requests.Session()
        configure_ssl_verification("Zephyr", "https://myzephyr.example.com/api", session, ssl_verify=False)
        # Check that adapter is mounted for the domain
        mounted = [k for k, v in session.adapters.items() if isinstance(v, SSLIgnoreAdapter)]
        assert any("myzephyr.example.com" in m for m in mounted)
