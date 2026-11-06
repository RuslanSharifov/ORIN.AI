"""Explicit allowlist for tools. Models never execute arbitrary Python or shell code."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any


class ToolError(Exception):
    """Base error for registry operations."""


class UnknownToolError(ToolError):
    """Raised when a tool is not registered."""


class ToolValidationError(ToolError):
    """Raised when tool arguments are invalid."""


class ToolPermissionError(ToolError):
    """Raised when a caller is missing a required permission."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[..., Any]
    permissions: frozenset[str] = field(default_factory=frozenset)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if not spec.name or not spec.name.isidentifier():
            raise ValueError("Tool names must be valid Python identifiers")
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def list_tools(self) -> tuple[ToolSpec, ...]:
        return tuple(self._tools.values())

    def execute(
        self,
        name: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        granted_permissions: frozenset[str] = frozenset(),
    ) -> Any:
        try:
            spec = self._tools[name]
        except KeyError as error:
            raise UnknownToolError(f"Unknown tool: {name}") from error

        if not spec.permissions.issubset(granted_permissions):
            raise ToolPermissionError(f"Permission denied for tool: {name}")

        arguments = {} if arguments is None else arguments
        if not isinstance(arguments, Mapping) or any(
            not isinstance(key, str) for key in arguments
        ):
            raise ToolValidationError("Arguments must be an object with string keys")
        try:
            return spec.handler(**arguments)
        except TypeError as error:
            raise ToolValidationError(f"Invalid arguments for {name}") from error
