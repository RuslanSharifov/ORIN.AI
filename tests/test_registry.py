import pytest

from orin.app import build_registry
from orin.core.registry import (
    ToolPermissionError,
    ToolRegistry,
    ToolSpec,
    ToolValidationError,
    UnknownToolError,
)


def test_builtin_tools_are_registered():
    assert {tool.name for tool in build_registry().list_tools()} == {
        "get_current_time",
        "get_ram_usage",
        "get_cpu_usage",
    }


def test_unknown_tool_is_blocked():
    with pytest.raises(UnknownToolError):
        build_registry().execute("run_shell")


def test_permission_denied_by_default():
    registry = ToolRegistry()
    registry.register(ToolSpec("private_action", "Restricted", lambda: True, frozenset({"admin"})))
    with pytest.raises(ToolPermissionError):
        registry.execute("private_action")
    assert registry.execute("private_action", granted_permissions=frozenset({"admin"})) is True


def test_invalid_argument_shape_is_rejected():
    with pytest.raises(ToolValidationError):
        build_registry().execute("get_current_time", {"unexpected": True})


def test_duplicate_registration_rejected():
    registry = ToolRegistry()
    registry.register(ToolSpec("clock", "Clock", lambda: "10:00"))
    with pytest.raises(ValueError):
        registry.register(ToolSpec("clock", "Clock", lambda: "11:00"))
