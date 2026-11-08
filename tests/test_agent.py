import pytest

from orin.app import build_registry
from orin.core.agent import Agent
from orin.core.contracts import ModelResponse, ToolCall
from orin.core.session import run_turn
from orin.providers.demo import DemoProvider


def test_allowed_tool_call():
    result = Agent(build_registry()).process(
        ModelResponse(tool_calls=(ToolCall("get_ram_usage", call_id="abc"),))
    )
    assert result.results[0].ok is True
    assert result.results[0].call_id == "abc"
    assert 0 <= result.results[0].data["percent"] <= 100


def test_unknown_tool_denied():
    result = Agent(build_registry()).process(
        ModelResponse(tool_calls=(ToolCall("run_shell", {"command": "whoami"}),))
    )
    assert result.results[0].ok is False
    assert "Unknown tool" in result.results[0].error


def test_invalid_arguments_rejected():
    result = Agent(build_registry()).process(
        ModelResponse(tool_calls=(ToolCall("get_current_time", {"x": 5}),))
    )
    assert result.results[0].ok is False


def test_bounded_tool_calls():
    with pytest.raises(ValueError):
        Agent(build_registry(), max_tool_calls=1).process(
            ModelResponse(tool_calls=(ToolCall("get_current_time"), ToolCall("get_ram_usage")))
        )


def test_demo_round_trip():
    outcome = run_turn(DemoProvider(), Agent(build_registry()), "RAM neçə faizdir?")
    assert outcome.results[0].ok
    assert "percent" in outcome.text



def test_unexpected_tool_failure_is_isolated():
    from orin.core.registry import ToolRegistry, ToolSpec

    def restricted():
        raise PermissionError(13, "Permission denied", "/proc/stat")

    registry = ToolRegistry()
    registry.register(ToolSpec("restricted", "Unsafe on Android", restricted))
    result = Agent(registry).process(ModelResponse(tool_calls=(ToolCall("restricted"),)))
    assert result.results[0].ok is False
    assert "unavailable" in result.results[0].error
    assert "/proc/stat" not in result.results[0].error
