"""Application context for the Zephyr MCP server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr_mcp.zephyr.config import ZephyrConfig


@dataclass(frozen=True)
class AppContext:
    """Context holding fully configured Zephyr configuration loaded from environment variables at server startup."""

    full_zephyr_config: ZephyrConfig | None = None
    read_only: bool = False
    enabled_tools: list[str] | None = None
