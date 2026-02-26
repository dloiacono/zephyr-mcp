# Zephyr Scale MCP Server

MCP (Model Context Protocol) server for **Zephyr Scale** test management — providing AI-powered access to test cases, test cycles, and test executions.

## Features

- **Test Cases**: Get, search, create, update, and link test cases to Jira issues
- **Test Cycles**: Get, create test cycles with planned dates and versions
- **Test Executions**: Get, create, update test execution results
- **Authentication**: Supports Personal Access Token (PAT), Basic Auth, and OAuth 2.0
- **Read-Only Mode**: Optional flag to prevent write operations

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

## Available Tools

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
