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
│  │                    MCP Tools Layer                         │ │
│  │                                                            │ │
│  │  zephyr_get_test_case    zephyr_search_test_cases          │ │
│  │  zephyr_create_test_case zephyr_update_test_case           │ │
│  │  zephyr_get_test_cycle   zephyr_create_test_cycle          │ │
│  │  zephyr_get_test_execution                                 │ │
│  │  zephyr_create_test_execution                              │ │
│  │  zephyr_update_test_execution                              │ │
│  │  zephyr_link_test_case_to_issue                            │ │
│  └────────────────┬──────────────────┬────────────────────────┘ │
│                   │                  │                           │
│  ┌────────────────▼──┐  ┌───────────▼────────────────────────┐  │
│  │  @check_write_    │  │     Dependency Injection           │  │
│  │  access Decorator │  │     get_zephyr_fetcher(ctx)        │  │
│  │  (read-only mode) │  │                                    │  │
│  └───────────────────┘  │  1. HTTP request context (SSE)     │  │
│                         │  2. Header-based PAT auth          │  │
│                         │  3. User-specific OAuth/PAT        │  │
│                         │  4. Global config fallback         │  │
│                         └──────────────┬─────────────────────┘  │
│                                        │                        │
│  ┌─────────────────────────────────────▼─────────────────────┐  │
│  │                   AppContext (Lifespan)                    │  │
│  │  full_zephyr_config: ZephyrConfig | None                  │  │
│  │  read_only: bool                                          │  │
│  │  enabled_tools: list[str] | None                          │  │
│  └─────────────────────────────────────┬─────────────────────┘  │
│                                        │                        │
│  ┌─────────────────────────────────────▼─────────────────────┐  │
│  │                 Server Factory                            │  │
│  │  create_server(read_only) -> FastMCP                      │  │
│  │  - Loads ZephyrConfig from environment                    │  │
│  │  - Sets up lifespan with AppContext                       │  │
│  │  - Registers all MCP tools                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ZephyrFetcher                              │
│            (TestCasesMixin + TestCyclesMixin                     │
│             + TestExecutionsMixin)                               │
│                                                                 │
│  ┌───────────────┐ ┌───────────────┐ ┌────────────────────────┐ │
│  │ TestCasesMixin│ │TestCyclesMixin│ │ TestExecutionsMixin    │ │
│  │               │ │               │ │                        │ │
│  │ get_test_case │ │ get_test_cycle│ │ get_test_execution     │ │
│  │ search_*      │ │ search_*      │ │ search_*               │ │
│  │ create_*      │ │ create_*      │ │ create_*               │ │
│  │ update_*      │ │ update_*      │ │ update_*               │ │
│  │ delete_*      │ │ delete_*      │ │ delete_*               │ │
│  │ link_to_issue │ │ link_to_issue │ │ get_results            │ │
│  └───────┬───────┘ └───────┬───────┘ └────────────┬───────────┘ │
│          └─────────────────┼──────────────────────┘             │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    ZephyrClient                             ││
│  │  - HTTP session (requests.Session)                         ││
│  │  - Authentication: OAuth / Bearer / PAT / Basic            ││
│  │  - SSL verification & client certs                         ││
│  │  - Proxy support (HTTP/HTTPS/SOCKS)                        ││
│  │  - Custom headers                                          ││
│  │  - get() / post() / put() / delete()                       ││
│  └──────────────────────────┬──────────────────────────────────┘│
└─────────────────────────────┼───────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Zephyr Scale REST API                         │
│              https://api.zephyrscale.smartbear.com/v2           │
│                                                                 │
│  /testcases  /testcycles  /testexecutions  /issuelinks          │
└─────────────────────────────────────────────────────────────────┘
```

## Package Structure

```
src/zephyr_mcp/
├── __init__.py              # CLI entry point (Click)
├── exceptions.py            # ZephyrAuthenticationError
├── server/
│   ├── __init__.py          # Re-exports create_server
│   ├── context.py           # AppContext dataclass
│   ├── dependencies.py      # get_zephyr_fetcher (async DI)
│   ├── factory.py           # create_server -> FastMCP
│   └── tools.py             # MCP tool definitions (10 tools)
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

## Transport Modes

- **stdio**: Default. Server communicates via stdin/stdout. Used for IDE integrations.
- **SSE**: Server-Sent Events over HTTP. Supports per-request authentication via headers.
