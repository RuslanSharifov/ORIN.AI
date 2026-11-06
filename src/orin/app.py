"""Application composition root. Future adapters belong behind interfaces."""

from orin.core.registry import ToolRegistry, ToolSpec
from orin.tools.system import get_cpu_usage, get_current_time, get_ram_usage


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("get_current_time", "Read the local computer clock", get_current_time)
    )
    registry.register(
        ToolSpec("get_ram_usage", "Read current RAM usage", get_ram_usage)
    )
    registry.register(
        ToolSpec("get_cpu_usage", "Read current CPU usage", get_cpu_usage)
    )
    return registry
