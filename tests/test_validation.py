import pytest

from orin.core.registry import ToolRegistry, ToolSpec, ToolValidationError


def make_registry():
    registry = ToolRegistry()

    def set_level(level: int, enabled: bool = False) -> int:
        return level if enabled else 0

    registry.register(ToolSpec("set_level", "Test input validation", set_level))
    return registry


def test_valid_typed_arguments():
    assert make_registry().execute("set_level", {"level": 4, "enabled": True}) == 4


@pytest.mark.parametrize(
    "arguments",
    [
        {"level": "4"},
        {"level": True},
        {"level": 1.5},
        {"level": 4, "enabled": "yes"},
        {"level": 4, "unknown": 1},
        {},
        {"level": 4, "enabled": False, "extra": None},
    ],
)
def test_invalid_arguments(arguments):
    with pytest.raises(ToolValidationError):
        make_registry().execute("set_level", arguments)


def test_no_variadic_tools():
    registry = ToolRegistry()

    def unsafe(**kwargs):
        return kwargs

    registry.register(ToolSpec("unsafe", "Reject variadic handlers", unsafe))
    with pytest.raises(ToolValidationError):
        registry.execute("unsafe", {"command": "hello"})


def test_handler_exceptions_are_not_mislabeled():
    registry = ToolRegistry()

    def broken() -> None:
        raise RuntimeError("real handler failure")

    registry.register(ToolSpec("broken", "Fails", broken))
    with pytest.raises(RuntimeError, match="real handler failure"):
        registry.execute("broken")
