"""SSL-related utility functions for the Zephyr MCP server."""

import logging
import ssl
from typing import Any
from urllib.parse import urlparse

from requests.adapters import HTTPAdapter
from requests.sessions import Session
from urllib3.poolmanager import PoolManager

logger = logging.getLogger("mcp-zephyr")


class SSLIgnoreAdapter(HTTPAdapter):
    """HTTP adapter that ignores SSL verification."""

    def init_poolmanager(self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: Any) -> None:
        """Initialize the connection pool manager with SSL verification disabled."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            **pool_kwargs,
        )

    def cert_verify(self, conn: Any, url: str, verify: bool, cert: Any | None) -> None:
        """Override cert verification to disable SSL verification."""
        super().cert_verify(conn, url, verify=False, cert=cert)


def configure_ssl_verification(
    service_name: str,
    url: str,
    session: Session,
    ssl_verify: bool,
    client_cert: str | None = None,
    client_key: str | None = None,
    client_key_password: str | None = None,
) -> None:
    """Configure SSL verification and client certificates for a service."""
    if isinstance(client_cert, str) and isinstance(client_key, str):
        if isinstance(client_key_password, str) and client_key_password:
            raise ValueError(
                f"{service_name} client certificate authentication with encrypted "
                "private keys is not supported. Please decrypt your private key first "
                "(e.g., using 'openssl rsa -in encrypted.key -out decrypted.key')."
            )

        session.cert = (client_cert, client_key)
        logger.info(f"{service_name} client certificate authentication configured with cert: {client_cert}")

    if not ssl_verify:
        logger.warning(f"{service_name} SSL verification disabled. This is insecure and should only be used in testing environments.")

        domain = urlparse(url).netloc
        adapter = SSLIgnoreAdapter()
        session.mount(f"https://{domain}", adapter)
        session.mount(f"http://{domain}", adapter)
