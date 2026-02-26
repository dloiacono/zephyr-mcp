"""Protocol definition for Zephyr Squad API clients."""

from typing import Any, Protocol


class SquadClientProtocol(Protocol):
    """Protocol that both JWT and PAT Squad clients implement."""

    def get(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]: ...

    def post(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]: ...

    def put(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]: ...

    def delete(self, endpoint: str, query_params: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]: ...
