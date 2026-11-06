"""Provider-independent tool execution coordinator.

The agent never evals model output. Tool errors are returned as data and
model-produced text is not trusted as permission to run system commands.
"""

from dataclasses import dataclass

from orin.core.contracts import ModelResponse, ToolResult
from orin.core.registry import ToolError, ToolRegistry


@dataclass(frozen=True)
class AgentOutcome:
    text: str
    results: tuple[ToolResult, ...]


class Agent:
    def __init__(self, registry: ToolRegistry, *, max_tool_calls: int = 5) -> None:
        if max_tool_calls < 1:
            raise ValueError("max_tool_calls must be positive")
        self.registry = registry
        self.max_tool_calls = max_tool_calls

    def process(
        self, response: ModelResponse, *, granted_permissions: frozenset[str] = frozenset()
    ) -> AgentOutcome:
        if len(response.tool_calls) > self.max_tool_calls:
            raise ValueError("Model requested too many tool calls")
        results: list[ToolResult] = []
        for call in response.tool_calls:
            try:
                data = self.registry.execute(
                    call.name, call.arguments, granted_permissions=granted_permissions
                )
            except ToolError as error:
                results.append(ToolResult(call.name, call.call_id, False, error=str(error)))
            else:
                results.append(ToolResult(call.name, call.call_id, True, data=data))
        return AgentOutcome(text=response.text, results=tuple(results))
