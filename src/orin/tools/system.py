"""Read-only system utilities."""

from datetime import datetime

import psutil


def get_current_time() -> str:
    """Return the actual local machine time in HH:MM format."""
    return datetime.now().astimezone().strftime("%H:%M")


def get_ram_usage() -> dict[str, float]:
    """Return observed memory usage; percentages are in [0, 100]."""
    memory = psutil.virtual_memory()
    return {
        "percent": float(memory.percent),
        "total_gb": round(memory.total / (1024**3), 2),
        "available_gb": round(memory.available / (1024**3), 2),
    }


def get_cpu_usage() -> dict[str, float]:
    """Return a short sampled CPU load percentage."""
    return {"percent": float(psutil.cpu_percent(interval=0.1))}
