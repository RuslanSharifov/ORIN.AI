import pytest

from orin.core.registry import ToolError
from orin.tools.system import get_cpu_usage, get_current_time, get_ram_usage


def test_time_is_hh_mm():
    value = get_current_time()
    assert len(value) == 5
    assert value[2] == ":"
    assert 0 <= int(value[:2]) <= 23
    assert 0 <= int(value[3:]) <= 59


def test_ram_values():
    result = get_ram_usage()
    assert 0 <= result["percent"] <= 100
    assert result["total_gb"] > 0
    assert 0 <= result["available_gb"] <= result["total_gb"]


def test_cpu_percentage():
    assert 0 <= get_cpu_usage()["percent"] <= 100



def test_cpu_permission_denied_on_android(monkeypatch):
    from orin.tools import system

    def denied(*, interval):
        raise PermissionError(13, "Permission denied", "/proc/stat")

    monkeypatch.setattr(system.psutil, "cpu_percent", denied)
    with pytest.raises(ToolError, match="CPU statistics are restricted"):
        system.get_cpu_usage()


def test_ram_permission_denied_on_android(monkeypatch):
    from orin.tools import system

    def denied():
        raise PermissionError(13, "Permission denied", "/proc/meminfo")

    monkeypatch.setattr(system.psutil, "virtual_memory", denied)
    with pytest.raises(ToolError, match="RAM statistics are restricted"):
        system.get_ram_usage()


def test_restricted_android_cpu_tool_returns_failure_not_traceback(monkeypatch):
    from orin.app import build_registry
    from orin.core.agent import Agent
    from orin.core.contracts import ModelResponse, ToolCall
    from orin.tools import system

    def denied(*, interval):
        raise PermissionError(13, "Permission denied", "/proc/stat")

    monkeypatch.setattr(system.psutil, "cpu_percent", denied)
    outcome = Agent(build_registry()).process(
        ModelResponse(tool_calls=(ToolCall("get_cpu_usage"),))
    )
    assert not outcome.results[0].ok
    assert "/proc/stat" not in str(outcome.results[0].error)
