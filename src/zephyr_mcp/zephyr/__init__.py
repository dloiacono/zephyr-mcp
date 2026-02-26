"""Zephyr Scale API client package."""

from zephyr_mcp.zephyr.client import ZephyrClient
from zephyr_mcp.zephyr.config import ZephyrConfig
from zephyr_mcp.zephyr.testcases import TestCasesMixin
from zephyr_mcp.zephyr.testcycles import TestCyclesMixin
from zephyr_mcp.zephyr.testexecutions import TestExecutionsMixin


class ZephyrFetcher(TestCasesMixin, TestCyclesMixin, TestExecutionsMixin):
    """Combined Zephyr Scale API client with all operations."""

    def __init__(self, config: ZephyrConfig | None = None) -> None:
        if config is None:
            config = ZephyrConfig.from_env()
        self.client = ZephyrClient(config)
        self.config = config


__all__ = [
    "ZephyrFetcher",
    "ZephyrClient",
    "ZephyrConfig",
    "TestCasesMixin",
    "TestCyclesMixin",
    "TestExecutionsMixin",
]
