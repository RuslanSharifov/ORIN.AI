"""Read-only system utilities, including restricted Android devices."""

from datetime import datetime

import psutil

from orin.core.registry import ToolError


def get_current_time() -> str:
    """Return the actual local machine time in HH:MM format."""
    return datetime.now().astimezone().strftime("%H:%M")


def get_ram_usage() -> dict[str, float]:
    """Read RAM usage, or report OS restrictions to the agent safely."""
    try:
        memory = psutil.virtual_memory()
    except (OSError, psutil.Error) as error:
        raise ToolError("RAM statistics are restricted on this device.") from error
    return {
        "percent": float(memory.percent),
        "total_gb": round(memory.total / (1024**3), 2),
        "available_gb": round(memory.available / (1024**3), 2),
    }


def get_cpu_usage() -> dict[str, float]:
    """Read CPU load, or report OS restrictions to the agent safely."""
    try:
        usage = psutil.cpu_percent(interval=0.1)
    except (OSError, psutil.Error) as error:
        raise ToolError("CPU statistics are restricted on this device.") from error
    return {"percent": float(usage)}
