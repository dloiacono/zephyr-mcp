# Zephyr MCP Server

MCP (Model Context Protocol) server for **Zephyr Scale** and **Zephyr Squad** test management — providing AI-powered access to test cases, test cycles, and test executions.

## Features

### Zephyr Scale

- **Test Cases**: Get, search, create, update, and link test cases to Jira issues
- **Test Cycles**: Get, create test cycles with planned dates and versions
- **Test Executions**: Get, create, update test execution results
- **Authentication**: Supports Personal Access Token (PAT), Basic Auth, and OAuth 2.0

### Zephyr Squad

- **Test Cycles**: Get, list, create, and manage Squad test cycles
- **Test Executions**: Get executions, add tests to cycles, update execution status
- **ZQL Search**: Execute Zephyr Query Language searches
- **Authentication**: JWT token auth (Cloud Connect API) or PAT/Basic Auth (Jira ZAPI)

### Common

- **Read-Only Mode**: Optional flag to prevent write operations
- **Dual Product Support**: Use Scale, Squad, or both simultaneously

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for package management
- [Task](https://taskfile.dev/) for task running (optional)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd zephyr-mcp

# Using Task (recommended)
task install

# Or manually
uv venv
uv pip install -e ".[dev]"
```

### Configuration

Set the following environment variables:

| Variable | Required | Description |
|---|---|---|
| `ZEPHYR_URL` | **Yes** | Zephyr Scale API base URL |
| `ZEPHYR_PERSONAL_TOKEN` | * | Personal Access Token |
| `ZEPHYR_EMAIL` | * | Email for basic auth |
| `ZEPHYR_API_TOKEN` | * | API token for basic auth |
| `ZEPHYR_PROJECT_KEY` | No | Default project key |
| `ZEPHYR_SSL_VERIFY` | No | SSL verification (default: `true`) |
| `ZEPHYR_HTTP_PROXY` | No | HTTP proxy URL |
| `ZEPHYR_HTTPS_PROXY` | No | HTTPS proxy URL |
| `ZEPHYR_SOCKS_PROXY` | No | SOCKS proxy URL |
| `ZEPHYR_CUSTOM_HEADERS` | No | Comma-separated `key=value` pairs |

\* At least one authentication method must be configured: PAT, Basic (email + api_token), or OAuth.

#### Zephyr Squad Configuration

Zephyr Squad supports **two authentication modes**. The mode is auto-detected based on which environment variables are set.

##### Option A: PAT Authentication (Jira ZAPI)

Uses Jira Personal Access Token against `/rest/zapi/latest/` endpoints.

| Variable | Required | Description |
|---|---|---|
| `ZEPHYR_SQUAD_PAT_TOKEN` | **Yes** | Jira Personal Access Token or API Token |
| `ZEPHYR_SQUAD_JIRA_BASE_URL` | **Yes** | Jira instance base URL (e.g., `https://your-domain.atlassian.net`) |
| `ZEPHYR_SQUAD_JIRA_EMAIL` | No | Email for Cloud Basic Auth (omit for Server/DC Bearer token) |
| `ZEPHYR_SQUAD_PROJECT_ID` | No | Default Jira project ID (numeric) |

##### Option B: JWT Authentication (Cloud Connect API)

Uses per-request JWT tokens against the Zephyr Squad Cloud Connect API.

| Variable | Required | Description |
|---|---|---|
| `ZEPHYR_SQUAD_ACCESS_KEY` | **Yes** | Zephyr Squad API access key |
| `ZEPHYR_SQUAD_SECRET_KEY` | **Yes** | Zephyr Squad API secret key |
| `ZEPHYR_SQUAD_ACCOUNT_ID` | **Yes** | Jira Cloud account ID |
| `ZEPHYR_SQUAD_PROJECT_ID` | No | Default Jira project ID (numeric) |
| `ZEPHYR_SQUAD_BASE_URL` | No | Squad API base URL (default: `https://prod-api.zephyr4jiracloud.com/connect`) |

You can find your access/secret keys in Jira under **Apps > Zephyr Squad > API Keys**.

> **Note:** If both `ZEPHYR_SQUAD_PAT_TOKEN` and `ZEPHYR_SQUAD_ACCESS_KEY` are set, PAT mode takes precedence.

#### OAuth Configuration

For OAuth 2.0 authentication, set:

| Variable | Description |
|---|---|
| `ATLASSIAN_OAUTH_CLIENT_ID` | OAuth client ID |
| `ATLASSIAN_OAUTH_CLIENT_SECRET` | OAuth client secret |
| `ATLASSIAN_OAUTH_REDIRECT_URI` | OAuth redirect URI |
| `ATLASSIAN_OAUTH_SCOPE` | OAuth scopes |
| `ATLASSIAN_OAUTH_CLOUD_ID` | Atlassian Cloud ID |
| `ATLASSIAN_OAUTH_ACCESS_TOKEN` | Pre-existing access token (BYO token mode) |

## Usage

### CLI

```bash
# Start with stdio transport (default)
zephyr-mcp

# Start with SSE transport
zephyr-mcp --transport sse --port 8000

# Read-only mode
zephyr-mcp --read-only

# Verbose logging
zephyr-mcp -vv
```

### MCP Client Configuration

Add to your MCP client config (e.g., Claude Desktop):

#### Using local installation

```json
{
  "mcpServers": {
    "zephyr": {
      "command": "zephyr-mcp",
      "env": {
        "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
        "ZEPHYR_PERSONAL_TOKEN": "your-token-here"
      }
    }
  }
}
```

#### Using Docker

```json
{
  "mcpServers": {
    "zephyr": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "ZEPHYR_URL",
        "-e", "ZEPHYR_PERSONAL_TOKEN",
        "ghcr.io/dloiacono/zephyr-mcp:latest",
        "--transport", "stdio"
      ],
      "env": {
        "ZEPHYR_URL": "https://api.zephyrscale.smartbear.com/v2",
        "ZEPHYR_PERSONAL_TOKEN": "your-token-here"
      }
    }
  }
}
```

#### Using Docker with Zephyr Squad (PAT)

```json
{
  "mcpServers": {
    "zephyr": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "ZEPHYR_SQUAD_PAT_TOKEN",
        "-e", "ZEPHYR_SQUAD_JIRA_BASE_URL",
        "-e", "ZEPHYR_SQUAD_JIRA_EMAIL",
        "ghcr.io/dloiacono/zephyr-mcp:latest",
        "--transport", "stdio"
      ],
      "env": {
        "ZEPHYR_SQUAD_PAT_TOKEN": "your-pat-or-api-token",
        "ZEPHYR_SQUAD_JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "ZEPHYR_SQUAD_JIRA_EMAIL": "your-email@example.com"
      }
    }
  }
}
```

#### Using Docker with Zephyr Squad (JWT)

```json
{
  "mcpServers": {
    "zephyr": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "ZEPHYR_SQUAD_ACCESS_KEY",
        "-e", "ZEPHYR_SQUAD_SECRET_KEY",
        "-e", "ZEPHYR_SQUAD_ACCOUNT_ID",
        "ghcr.io/dloiacono/zephyr-mcp:latest",
        "--transport", "stdio"
      ],
      "env": {
        "ZEPHYR_SQUAD_ACCESS_KEY": "your-access-key",
        "ZEPHYR_SQUAD_SECRET_KEY": "your-secret-key",
        "ZEPHYR_SQUAD_ACCOUNT_ID": "your-account-id"
      }
    }
  }
}
```

You can also run the Docker image as a standalone SSE server:

```bash
docker run -p 8000:8000 \
  -e ZEPHYR_URL=https://api.zephyrscale.smartbear.com/v2 \
  -e ZEPHYR_PERSONAL_TOKEN=your-token-here \
  ghcr.io/dloiacono/zephyr-mcp:latest
```

## Available Tools

### Zephyr Scale Tools

| Tool | Description | Write |
|---|---|---|
| `zephyr_get_test_case` | Get a test case by key | No |
| `zephyr_search_test_cases` | Search test cases in a project | No |
| `zephyr_create_test_case` | Create a new test case | Yes |
| `zephyr_update_test_case` | Update an existing test case | Yes |
| `zephyr_get_test_cycle` | Get a test cycle by key | No |
| `zephyr_create_test_cycle` | Create a new test cycle | Yes |
| `zephyr_get_test_execution` | Get a test execution by ID | No |
| `zephyr_create_test_execution` | Create a new test execution | Yes |
| `zephyr_update_test_execution` | Update a test execution | Yes |
| `zephyr_link_test_case_to_issue` | Link test case to Jira issue | Yes |

### Zephyr Squad Tools

| Tool | Description | Write |
|---|---|---|
| `squad_get_cycle` | Get a Squad test cycle by ID | No |
| `squad_get_cycles` | List all cycles for a project | No |
| `squad_create_cycle` | Create a new Squad test cycle | Yes |
| `squad_get_execution` | Get a Squad test execution by ID | No |
| `squad_get_executions_by_cycle` | Get all executions for a cycle | No |
| `squad_add_test_to_cycle` | Add a test (Jira issue) to a cycle | Yes |
| `squad_update_execution` | Update execution status/comment | Yes |
| `squad_zql_search` | Execute a ZQL search query | No |

## Development

```bash
# Format code
task format

# Lint and auto-fix
task check

# Run tests
task test

# Run tests with coverage
task test-cov
```

## License

MIT
