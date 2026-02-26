"""Zephyr Squad API client package."""

from zephyr_mcp.squad.client import ZephyrSquadClient
from zephyr_mcp.squad.config import ZephyrSquadConfig
from zephyr_mcp.squad.cycles import SquadCyclesMixin
from zephyr_mcp.squad.executions import SquadExecutionsMixin


class SquadFetcher(SquadCyclesMixin, SquadExecutionsMixin):
    """Combined Zephyr Squad API client with all operations."""

    def __init__(self, config: ZephyrSquadConfig | None = None) -> None:
        if config is None:
            config = ZephyrSquadConfig.from_env()
        self.client = ZephyrSquadClient(config)
        self.config = config


__all__ = [
    "SquadFetcher",
    "ZephyrSquadClient",
    "ZephyrSquadConfig",
    "SquadCyclesMixin",
    "SquadExecutionsMixin",
]
