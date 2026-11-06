"""Offline deterministic provider used for learning and tests, not an LLM."""

from orin.core.contracts import ModelResponse, ToolCall, ToolResult


class DemoProvider:
    def respond(
        self, user_message: str, *, tool_results: tuple[ToolResult, ...] = ()
    ) -> ModelResponse:
        if tool_results:
            result = tool_results[0]
            return ModelResponse(
                text=str(result.data) if result.ok else f"Tool error: {result.error}"
            )
        message = user_message.casefold()
        if "ram" in message:
            return ModelResponse(tool_calls=(ToolCall("get_ram_usage"),))
        if "cpu" in message or "prosessor" in message:
            return ModelResponse(tool_calls=(ToolCall("get_cpu_usage"),))
        if "saat" in message or "time" in message:
            return ModelResponse(tool_calls=(ToolCall("get_current_time"),))
        return ModelResponse(text="Demo rejimi: saat, RAM və ya CPU barədə soruş.")
