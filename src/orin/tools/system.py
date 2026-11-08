"""Read-only system utilities."""

from datetime import datetime

import psutil

from orin.core.registry import ToolError


def get_current_time() -> str:
    """Return the actual local machine time in HH:MM format."""
    return datetime.now().astimezone().strftime("%H:%M")


def get_ram_usage() -> dict[str, float | str]:
    """Return observed memory usage; percentages are in [0, 100]."""
    try:
        try:
        memory = psutil.virtual_memory()
    except (OSError, psutil.Error) as error:
        raise ToolError("RAM məlumatına bu cihazda giriş məhduddur.") from error
    except (OSError, psutil.Error):
        return {"status": "unavailable", "reason": "Memory metrics are restricted on this device"}
    return {
        "percent": float(memory.percent),
        "total_gb": round(memory.total / (1024**3), 2),
        "available_gb": round(memory.available / (1024**3), 2),
    }


def get_cpu_usage() -> dict[str, float | str]:
    """Return a short sampled CPU load percentage."""
    try:
        try:
        usage = psutil.cpu_percent(interval=0.1)
    except (OSError, psutil.Error) as error:
        raise ToolError("CPU məlumatına bu cihazda giriş məhduddur.") from error
    return {"percent": float(usage)}
    except (OSError, psutil.Error):
        return {"status": "unavailable", "reason": "CPU usage is restricted on this device"}
