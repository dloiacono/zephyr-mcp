"""Configuration for the Zephyr Squad API client."""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger("mcp-zephyr-squad")

SQUAD_BASE_URL = "https://prod-api.zephyr4jiracloud.com/connect"

AUTH_TYPE_JWT = "jwt"
AUTH_TYPE_PAT = "pat"


@dataclass
class ZephyrSquadConfig:
    """Configuration for the Zephyr Squad API client.

    Supports two authentication modes:
    - **JWT** (Cloud Connect API): Uses access_key, secret_key, and account_id
      to generate per-request JWT tokens. Endpoints: /public/rest/api/1.0/
    - **PAT** (Jira ZAPI): Uses a Jira Personal Access Token against the
      /rest/zapi/latest/ endpoints on your Jira instance.
    """

    auth_type: str = AUTH_TYPE_JWT
    base_url: str = SQUAD_BASE_URL
    access_key: str | None = None
    secret_key: str | None = None
    account_id: str | None = None
    project_id: str | None = None
    # PAT-specific fields
    jira_base_url: str | None = None
    pat_token: str | None = None
    jira_email: str | None = None

    @classmethod
    def from_env(cls) -> "ZephyrSquadConfig":
        """Create configuration from environment variables.

        Auto-detects auth mode:
        - If ZEPHYR_SQUAD_PAT_TOKEN is set → PAT mode
        - If ZEPHYR_SQUAD_ACCESS_KEY is set → JWT mode
        """
        pat_token = os.getenv("ZEPHYR_SQUAD_PAT_TOKEN")
        jira_base_url = os.getenv("ZEPHYR_SQUAD_JIRA_BASE_URL")
        jira_email = os.getenv("ZEPHYR_SQUAD_JIRA_EMAIL")

        access_key = os.getenv("ZEPHYR_SQUAD_ACCESS_KEY")
        secret_key = os.getenv("ZEPHYR_SQUAD_SECRET_KEY")
        account_id = os.getenv("ZEPHYR_SQUAD_ACCOUNT_ID")
        project_id = os.getenv("ZEPHYR_SQUAD_PROJECT_ID")
        base_url = os.getenv("ZEPHYR_SQUAD_BASE_URL", SQUAD_BASE_URL)

        if pat_token:
            return cls._build_pat_config(pat_token, jira_base_url, jira_email, project_id)

        if access_key:
            return cls._build_jwt_config(access_key, secret_key, account_id, base_url, project_id)

        raise ValueError(
            "Zephyr Squad configuration requires either ZEPHYR_SQUAD_PAT_TOKEN (PAT mode) or ZEPHYR_SQUAD_ACCESS_KEY (JWT mode) to be set."
        )

    @classmethod
    def _build_pat_config(
        cls,
        pat_token: str,
        jira_base_url: str | None,
        jira_email: str | None,
        project_id: str | None,
    ) -> "ZephyrSquadConfig":
        if not jira_base_url:
            raise ValueError("ZEPHYR_SQUAD_JIRA_BASE_URL is required for PAT authentication.")

        logger.info(f"Zephyr Squad PAT configuration loaded: jira_base_url={jira_base_url}")

        return cls(
            auth_type=AUTH_TYPE_PAT,
            jira_base_url=jira_base_url.rstrip("/"),
            pat_token=pat_token,
            jira_email=jira_email,
            project_id=project_id,
        )

    @classmethod
    def _build_jwt_config(
        cls,
        access_key: str,
        secret_key: str | None,
        account_id: str | None,
        base_url: str,
        project_id: str | None,
    ) -> "ZephyrSquadConfig":
        if not secret_key:
            raise ValueError("ZEPHYR_SQUAD_SECRET_KEY environment variable is required for JWT authentication.")
        if not account_id:
            raise ValueError("ZEPHYR_SQUAD_ACCOUNT_ID environment variable is required for JWT authentication.")

        logger.info(f"Zephyr Squad JWT configuration loaded: base_url={base_url}, account_id={account_id}")

        return cls(
            auth_type=AUTH_TYPE_JWT,
            base_url=base_url,
            access_key=access_key,
            secret_key=secret_key,
            account_id=account_id,
            project_id=project_id,
        )
