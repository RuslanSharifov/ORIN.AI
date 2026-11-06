"""Explicit allowlist for tools. Models never execute arbitrary code."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from orin.core.validation import InvalidToolArguments, validate_arguments


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
        if not isinstance(arguments, Mapping):
            raise ToolValidationError("Arguments must be an object")
        try:
            validated = validate_arguments(spec.handler, arguments)
        except InvalidToolArguments as error:
            raise ToolValidationError(str(error)) from error
        return spec.handler(**validated)
