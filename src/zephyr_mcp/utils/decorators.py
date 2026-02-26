"""Decorators for the Zephyr MCP server."""

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from fastmcp import Context

logger = logging.getLogger(__name__)


F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def check_write_access(func: F) -> F:
    """Decorator for FastMCP tools to check if the application is in read-only mode."""

    @wraps(func)
    async def wrapper(ctx: Context, *args: Any, **kwargs: Any) -> Any:
        lifespan_ctx_dict = ctx.request_context.lifespan_context
        app_lifespan_ctx = lifespan_ctx_dict.get("app_lifespan_context") if isinstance(lifespan_ctx_dict, dict) else None

        if app_lifespan_ctx is not None and app_lifespan_ctx.read_only:
            tool_name = func.__name__
            action_description = tool_name.replace("_", " ")
            logger.warning(f"Attempted to call tool '{tool_name}' in read-only mode.")
            raise ValueError(f"Cannot {action_description} in read-only mode.")

        return await func(ctx, *args, **kwargs)

    return wrapper  # type: ignore
