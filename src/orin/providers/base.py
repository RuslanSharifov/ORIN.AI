"""Minimal adapter interface. No provider SDK is required by core."""

from typing import Protocol

from orin.core.contracts import ModelResponse, ToolResult


class AIProvider(Protocol):
    def respond(
        self, user_message: str, *, tool_results: tuple[ToolResult, ...] = ()
    ) -> ModelResponse:
        """Produce text and optional structured tool calls."""
        ...
