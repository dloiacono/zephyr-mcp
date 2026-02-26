"""Exceptions for the Zephyr MCP server."""


class ZephyrAuthenticationError(Exception):
    """Raised when Zephyr Scale API authentication fails (401/403)."""

    pass
