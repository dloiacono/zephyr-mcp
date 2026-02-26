"""Environment variable utility functions for the Zephyr MCP server."""

import os


def is_env_truthy(env_var_name: str, default: str = "") -> bool:
    """Check if environment variable is set to a standard truthy value."""
    return os.getenv(env_var_name, default).lower() in ("true", "1", "yes")


def is_env_extended_truthy(env_var_name: str, default: str = "") -> bool:
    """Check if environment variable is set to an extended truthy value."""
    return os.getenv(env_var_name, default).lower() in ("true", "1", "yes", "y", "on")


def is_env_ssl_verify(env_var_name: str, default: str = "true") -> bool:
    """Check SSL verification setting with secure defaults."""
    return os.getenv(env_var_name, default).lower() not in ("false", "0", "no")


def get_custom_headers(env_var_name: str) -> dict[str, str]:
    """Parse custom headers from environment variable containing comma-separated key=value pairs."""
    header_string = os.getenv(env_var_name)
    if not header_string or not header_string.strip():
        return {}

    headers = {}
    pairs = header_string.split(",")

    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            continue

        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key:
            headers[key] = value

    return headers
