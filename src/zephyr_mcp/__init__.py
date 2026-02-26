"""Zephyr Scale MCP Server.

Provides AI-powered access to Zephyr Scale test management through
the Model Context Protocol (MCP).
"""

import logging
import sys

import click


def main() -> None:
    """Entry point for the zephyr-mcp CLI."""
    _cli()


@click.command("zephyr-mcp")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="MCP transport type")
@click.option("--port", type=int, default=8000, help="Port for SSE transport")
@click.option("--host", type=str, default="0.0.0.0", help="Host for SSE transport")  # noqa: S104
@click.option("--read-only", is_flag=True, default=False, help="Run in read-only mode")
@click.option("-v", "--verbose", count=True, help="Increase logging verbosity (-v for INFO, -vv for DEBUG)")
def _cli(transport: str, port: int, host: str, read_only: bool, verbose: int) -> None:
    """Start the Zephyr Scale MCP server."""
    from zephyr_mcp.server import create_server

    log_level = logging.WARNING
    if verbose == 1:
        log_level = logging.INFO
    elif verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level, stream=sys.stderr, format="%(levelname)s - %(name)s - %(message)s")

    server = create_server(read_only=read_only)

    if transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(transport="sse", host=host, port=port)
