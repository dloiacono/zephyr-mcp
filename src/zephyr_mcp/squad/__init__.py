"""Zephyr Squad API client package."""

from zephyr_mcp.squad.client import ZephyrSquadClient
from zephyr_mcp.squad.config import AUTH_TYPE_PAT, ZephyrSquadConfig
from zephyr_mcp.squad.cycles import SquadCyclesMixin
from zephyr_mcp.squad.executions import SquadExecutionsMixin
from zephyr_mcp.squad.pat_client import ZephyrSquadPatClient


def _create_squad_client(config: ZephyrSquadConfig) -> ZephyrSquadClient | ZephyrSquadPatClient:
    """Create the appropriate Squad client based on auth_type."""
    if config.auth_type == AUTH_TYPE_PAT:
        return ZephyrSquadPatClient(config)
    return ZephyrSquadClient(config)


class SquadFetcher(SquadCyclesMixin, SquadExecutionsMixin):
    """Combined Zephyr Squad API client with all operations.

    Automatically selects JWT or PAT client based on config.auth_type.
    """

    def __init__(self, config: ZephyrSquadConfig | None = None) -> None:
        if config is None:
            config = ZephyrSquadConfig.from_env()
        self.client = _create_squad_client(config)
        self.config = config


__all__ = [
    "SquadFetcher",
    "ZephyrSquadClient",
    "ZephyrSquadPatClient",
    "ZephyrSquadConfig",
    "SquadCyclesMixin",
    "SquadExecutionsMixin",
]
