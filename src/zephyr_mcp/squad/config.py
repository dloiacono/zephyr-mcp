"""Configuration for the Zephyr Squad API client."""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger("mcp-zephyr-squad")

SQUAD_BASE_URL = "https://prod-api.zephyr4jiracloud.com/connect"


@dataclass
class ZephyrSquadConfig:
    """Configuration for the Zephyr Squad Cloud API client."""

    base_url: str = SQUAD_BASE_URL
    access_key: str | None = None
    secret_key: str | None = None
    account_id: str | None = None
    project_id: str | None = None

    @classmethod
    def from_env(cls) -> "ZephyrSquadConfig":
        """Create configuration from environment variables."""
        access_key = os.getenv("ZEPHYR_SQUAD_ACCESS_KEY")
        secret_key = os.getenv("ZEPHYR_SQUAD_SECRET_KEY")
        account_id = os.getenv("ZEPHYR_SQUAD_ACCOUNT_ID")
        project_id = os.getenv("ZEPHYR_SQUAD_PROJECT_ID")
        base_url = os.getenv("ZEPHYR_SQUAD_BASE_URL", SQUAD_BASE_URL)

        if not access_key:
            raise ValueError("ZEPHYR_SQUAD_ACCESS_KEY environment variable is required but not set.")
        if not secret_key:
            raise ValueError("ZEPHYR_SQUAD_SECRET_KEY environment variable is required but not set.")
        if not account_id:
            raise ValueError("ZEPHYR_SQUAD_ACCOUNT_ID environment variable is required but not set.")

        logger.info(f"Zephyr Squad configuration loaded: base_url={base_url}, account_id={account_id}")

        return cls(
            base_url=base_url,
            access_key=access_key,
            secret_key=secret_key,
            account_id=account_id,
            project_id=project_id,
        )
