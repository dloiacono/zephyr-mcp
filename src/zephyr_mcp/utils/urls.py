"""URL-related utility functions for the Zephyr MCP server."""

from urllib.parse import urlparse


def is_atlassian_cloud_url(url: str | None) -> bool:
    """Determine if a URL belongs to Atlassian Cloud or Server/Data Center."""
    if url is None or not url:
        return False

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""

    if hostname in ("localhost",) or hostname.startswith(("127.", "192.168.", "10.")):
        return False

    if hostname.startswith("172."):
        parts = hostname.split(".")
        if len(parts) >= 2:
            try:
                second_octet = int(parts[1])
                if 16 <= second_octet <= 31:
                    return False
            except ValueError:
                pass

    return (
        ".atlassian.net" in hostname
        or ".jira.com" in hostname
        or ".jira-dev.com" in hostname
        or "api.atlassian.com" in hostname
        or ".atlassian-us-gov-mod.net" in hostname
        or ".atlassian-us-gov.net" in hostname
        or "zephyrscale.smartbear.com" in hostname
    )
