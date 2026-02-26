# Zephyr MCP Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Client (LLM)                          │
│                   (Claude, Cursor, etc.)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ MCP Protocol (stdio / SSE)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastMCP Server                             │
│                    "Zephyr Scale MCP"                           │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              MCP Tools Layer (Scale + Squad)               │ │
│  │                                                            │ │
│  │  Zephyr Scale:                    Zephyr Squad:            │ │
│  │  zephyr_get_test_case             squad_get_cycle           │ │
│  │  zephyr_search_test_cases         squad_get_cycles          │ │
│  │  zephyr_create_test_case          squad_create_cycle        │ │
│  │  zephyr_update_test_case          squad_get_execution       │ │
│  │  zephyr_get_test_cycle            squad_get_executions_*    │ │
│  │  zephyr_create_test_cycle         squad_add_test_to_cycle   │ │
│  │  zephyr_get_test_execution        squad_update_execution    │ │
│  │  zephyr_create_test_execution     squad_zql_search          │ │
│  │  zephyr_update_test_execution                              │ │
│  │  zephyr_link_test_case_to_issue                            │ │
│  └──────────────────┬──────────────────┬────────────────────────┘ │
│                   │                  │                           │
│  ┌────────────────▼──┐  ┌───────────▼────────────────────┐  │
│  │  @check_write_    │  │     Dependency Injection           │  │
│  │  access Decorator │  │  get_zephyr_fetcher(ctx)  (Scale)  │  │
│  │  (read-only mode) │  │  get_squad_fetcher(ctx)   (Squad)  │  │
│  └───────────────────┘  │                                    │  │
│                         │  1. Lifespan config context        │  │
│                         │  2. Environment variable fallback  │  │
│                         └──────────────┬─────────────────────┘  │
│                                        │                        │
│  ┌─────────────────────────────────────▼─────────────────────┐  │
│  │                   AppContext (Lifespan)                    │  │
│  │  full_zephyr_config: ZephyrConfig | None    (Scale)        │  │
│  │  squad_config: ZephyrSquadConfig | None     (Squad)        │  │
│  │  read_only: bool                                          │  │
│  │  enabled_tools: list[str] | None                          │  │
│  └─────────────────────────────────────┬─────────────────────┘  │
│                                        │                        │
│  ┌─────────────────────────────────────▼─────────────────────┐  │
│  │                 Server Factory                            │  │
│  │  create_server(read_only) -> FastMCP                      │  │
│  │  - Loads ZephyrConfig + ZephyrSquadConfig from env        │  │
│  │  - Sets up lifespan with AppContext                       │  │
│  │  - Registers Scale + Squad MCP tools                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
┌──────────────────────────────┐ ┌────────────────────────────────┐
│       ZephyrFetcher            │ │         SquadFetcher            │
│  (TestCasesMixin               │ │  (SquadCyclesMixin              │
│   + TestCyclesMixin            │ │   + SquadExecutionsMixin)       │
│   + TestExecutionsMixin)       │ │                                │
│                                │ │  ┌────────────────────────────┐ │
│  ┌──────────────────────────┐ │ │  │  SquadCyclesMixin             │ │
│  │  ZephyrClient              │ │ │  │  get/create/update/delete    │ │
│  │  OAuth / PAT / Basic       │ │ │  └────────────────────────────┘ │
│  │  SSL / Proxy               │ │ │  ┌────────────────────────────┐ │
│  └──────────────────────────┘ │ │  │  SquadExecutionsMixin         │ │
│              │                   │ │  │  get/add/update/zql_search  │ │
└──────────────┼───────────────────┘ │  └────────────────────────────┘ │
              │                     │  ┌────────────────────────────┐ │
              │                     │  │  _create_squad_client()       │ │
              │                     │  │  (auto-selects by auth_type)  │ │
              │                     │  ├────────────────────────────┤ │
              │                     │  │  ZephyrSquadClient (JWT)      │ │
              │                     │  │  JWT auth (per-request)       │ │
              │                     │  │  HMAC-SHA256 canonical path   │ │
              │                     │  ├────────────────────────────┤ │
              │                     │  │  ZephyrSquadPatClient (PAT)   │ │
              │                     │  │  Bearer token or Basic Auth   │ │
              │                     │  │  Jira ZAPI endpoints          │ │
              │                     │  └─────────────┬──────────────┘ │
              │                     └──────────────┼─────────────────┘
              │ HTTPS                            │ HTTPS
              ▼                                   ▼
┌──────────────────────────────┐ ┌────────────────────────────────┐
│  Zephyr Scale REST API         │ │  Zephyr Squad APIs               │
│  api.zephyrscale.smartbear.com │ │                                  │
│                                │ │  JWT: Cloud Connect API          │
│  /testcases  /testcycles       │ │  prod-api.zephyr4jiracloud.com   │
│  /testexecutions  /issuelinks  │ │  /public/rest/api/1.0/           │
│                                │ │                                  │
│                                │ │  PAT: Jira ZAPI                  │
│                                │ │  your-jira.atlassian.net         │
│                                │ │  /rest/zapi/latest/              │
└──────────────────────────────┘ └────────────────────────────────┘
```

## Package Structure

```
src/zephyr_mcp/
├── __init__.py              # CLI entry point (Click)
├── exceptions.py            # ZephyrAuthenticationError
├── server/
│   ├── __init__.py          # Re-exports create_server
│   ├── context.py           # AppContext dataclass (Scale + Squad configs)
│   ├── dependencies.py      # get_zephyr_fetcher (async DI, Scale)
│   ├── squad_dependencies.py # get_squad_fetcher (async DI, Squad)
│   ├── factory.py           # create_server -> FastMCP (registers both)
│   ├── tools.py             # Zephyr Scale MCP tools (10 tools)
│   └── squad_tools.py       # Zephyr Squad MCP tools (8 tools)
├── squad/
│   ├── __init__.py          # SquadFetcher, _create_squad_client exports
│   ├── client.py            # ZephyrSquadClient (JWT HTTP transport)
│   ├── pat_client.py        # ZephyrSquadPatClient (PAT/Basic Auth)
│   ├── protocol.py          # SquadClientProtocol (interface)
│   ├── config.py            # ZephyrSquadConfig (dual auth: jwt|pat)
│   ├── jwt_auth.py          # JWT token generation (HMAC-SHA256)
│   ├── cycles.py            # SquadCyclesMixin
│   └── executions.py        # SquadExecutionsMixin
├── utils/
│   ├── __init__.py
│   ├── decorators.py        # @check_write_access
│   ├── env.py               # Environment variable helpers
│   ├── logging.py           # Logging setup, sensitive masking
│   ├── oauth.py             # OAuth 2.0 config & session mgmt
│   ├── ssl.py               # SSL verification & adapters
│   └── urls.py              # URL classification helpers
└── zephyr/
    ├── __init__.py           # ZephyrFetcher, ZephyrConfig exports
    ├── client.py             # ZephyrClient (HTTP transport)
    ├── config.py             # ZephyrConfig dataclass
    ├── constants.py          # Status/priority enums
    ├── testcases.py          # TestCasesMixin
    ├── testcycles.py         # TestCyclesMixin
    └── testexecutions.py     # TestExecutionsMixin
```

## Authentication Flow

### Zephyr Scale

```
Environment Variables
        │
        ▼
┌─────────────────────┐     ┌──────────────────┐
│  ZephyrConfig       │     │  OAuthConfig      │
│  .from_env()        │────▶│  (if OAuth)       │
│                     │     │  - client_id      │
│  auth_type:         │     │  - client_secret  │
│  - "oauth"          │     │  - token_url      │
│  - "bearer"         │     │  - cloud_id       │
│  - "pat"            │     └──────────────────┘
│  - "basic"          │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  ZephyrClient       │
│  Session headers:   │
│  - OAuth: Bearer    │
│  - PAT: Bearer      │
│  - Basic: user:pass │
└─────────────────────┘
```

### Zephyr Squad

Auto-detects auth mode based on environment variables:

```
Environment Variables
        │
        ▼
┌──────────────────────────────────┐
│  ZephyrSquadConfig.from_env()      │
│                                    │
│  ZEPHYR_SQUAD_PAT_TOKEN set?       │
│  ├─ Yes → auth_type = "pat"        │
│  │   jira_base_url, pat_token,     │
│  │   jira_email (optional)         │
│  └─ No  → auth_type = "jwt"        │
│       access_key, secret_key,      │
│       account_id                   │
└──────────────┬───────────────────┘
               │
      ┌────────┴─────────┐
      ▼                  ▼
┌───────────────┐  ┌───────────────────┐
│ PAT Client      │  │ JWT Client          │
│ Bearer / Basic  │  │ Per-request JWT:    │
│ /rest/zapi/     │  │ 1. Canonical path   │
│ latest/         │  │ 2. SHA-256 → qsh    │
│                 │  │ 3. HS256 encode     │
│                 │  │ 4. Header: JWT <t>  │
└───────────────┘  └───────────────────┘
```

## Transport Modes

- **stdio**: Default. Server communicates via stdin/stdout. Used for IDE integrations.
- **SSE**: Server-Sent Events over HTTP. Supports per-request authentication via headers.
