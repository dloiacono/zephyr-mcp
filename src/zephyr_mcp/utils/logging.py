"""Logging utilities for the Zephyr MCP server."""

import logging
import sys
from typing import TextIO


def setup_logging(level: int = logging.WARNING, stream: TextIO = sys.stderr) -> logging.Logger:
    """Configure Zephyr MCP logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    for logger_name in ["mcp-zephyr", "mcp.server"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

    return logging.getLogger("mcp-zephyr")


def mask_sensitive(value: str | None, keep_chars: int = 4) -> str:
    """Masks sensitive strings for logging."""
    if not value:
        return "Not Provided"
    if len(value) <= keep_chars * 2:
        return "*" * len(value)
    start = value[:keep_chars]
    end = value[-keep_chars:]
    middle = "*" * (len(value) - keep_chars * 2)
    return f"{start}{middle}{end}"


def get_masked_session_headers(headers: dict[str, str]) -> dict[str, str]:
    """Get session headers with sensitive values masked for safe logging."""
    sensitive_headers = {"Authorization", "Cookie", "Set-Cookie", "Proxy-Authorization"}
    masked_headers = {}

    for key, value in headers.items():
        if key in sensitive_headers:
            if key == "Authorization":
                if value.startswith("Basic "):
                    masked_headers[key] = f"Basic {mask_sensitive(value[6:])}"
                elif value.startswith("Bearer "):
                    masked_headers[key] = f"Bearer {mask_sensitive(value[7:])}"
                else:
                    masked_headers[key] = mask_sensitive(value)
            else:
                masked_headers[key] = mask_sensitive(value)
        else:
            masked_headers[key] = str(value)

    return masked_headers
