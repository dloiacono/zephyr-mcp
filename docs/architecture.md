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
              │                     │  │  ZephyrSquadClient          │ │
              │                     │  │  JWT auth (per-request)     │ │
              │                     │  │  HMAC-SHA256 canonical path │ │
              │                     │  └─────────────┬──────────────┘ │
              │                     └──────────────┼─────────────────┘
              │ HTTPS                            │ HTTPS
              ▼                                   ▼
┌──────────────────────────────┐ ┌────────────────────────────────┐
│  Zephyr Scale REST API         │ │  Zephyr Squad Cloud REST API    │
│  api.zephyrscale.smartbear.com │ │  prod-api.zephyr4jiracloud.com  │
│                                │ │                                │
│  /testcases  /testcycles       │ │  /cycle  /execution             │
│  /testexecutions  /issuelinks  │ │  /cycles/search                 │
│                                │ │  /zql/executeSearch             │
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
│   ├── __init__.py          # SquadFetcher, ZephyrSquadConfig exports
│   ├── client.py            # ZephyrSquadClient (JWT HTTP transport)
│   ├── config.py            # ZephyrSquadConfig dataclass
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

```
Environment Variables
        │
        ▼
┌──────────────────────────────┐
│  ZephyrSquadConfig             │
│  .from_env()                   │
│                                │
│  access_key (ZEPHYR_SQUAD_*)   │
│  secret_key                    │
│  account_id                    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  ZephyrSquadClient             │
│  Per-request JWT generation:   │
│  1. Build canonical path       │
│     METHOD&PATH&PARAMS         │
│  2. SHA-256 hash -> qsh        │
│  3. JWT encode (HS256)         │
│  4. Header: JWT <token>        │
└──────────────────────────────┘
```

## Transport Modes

- **stdio**: Default. Server communicates via stdin/stdout. Used for IDE integrations.
- **SSE**: Server-Sent Events over HTTP. Supports per-request authentication via headers.
