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
    result = system.get_cpu_usage()
    assert result["status"] == "unavailable"
    assert "percent" not in result
    assert "/proc/stat" not in str(result)


def test_ram_permission_denied_on_android(monkeypatch):
    from orin.tools import system

    def denied():
        raise PermissionError(13, "Permission denied", "/proc/meminfo")

    monkeypatch.setattr(system.psutil, "virtual_memory", denied)
    result = system.get_ram_usage()
    assert result["status"] == "unavailable"
    assert "/proc/meminfo" not in str(result)
