from types import SimpleNamespace
from typing import Tuple, cast

import psutil
import pytest

from src.core.monitor import Monitor
from src.models.metrics import CpuUsage, MemoryUsage


class _FakeProc:
    def __init__(self):
        self._cpu_calls = 0
        self.pid = 9999

    def cpu_percent(self, interval=None):
        # First call is priming; subsequent calls return deterministic value
        self._cpu_calls += 1
        return 120.0

    def cpu_times(self):
        return SimpleNamespace(user=1.0, system=0.5)

    def memory_info(self):
        return SimpleNamespace(rss=100 * 1024**2, vms=150 * 1024**2)


@pytest.fixture(autouse=True)
def _patch_psutil(monkeypatch):
    monkeypatch.setattr(psutil, "cpu_count", lambda logical=True: 4)
    monkeypatch.setattr(psutil, "Process", lambda pid: _FakeProc())


def test_collect_exact_samples(monkeypatch):
    # Make sleep a no-op and control monotonic
    t = {"val": 0.0}

    def fake_mono():
        v = t["val"]
        t["val"] += 1.0
        return v

    monkeypatch.setattr("src.core.monitor.monotonic", fake_mono)
    monkeypatch.setattr("src.core.monitor.sleep", lambda s: None)

    m = Monitor(pid=1234, interval=0.01)
    result = m.get_process_usage_by_interval(duration=0, samples=3, extended=False)

    assert len(result) == 3
    # CPU per-core should be 120 / 4 = 30
    cpu0, mem0 = cast(Tuple[CpuUsage, MemoryUsage], result[0])
    assert round(cpu0.process, 2) == 30.00
    assert mem0.rss == pytest.approx(100.0, abs=0.01)

    # sample_times should start at 0 and be increasing
    assert m.sample_times[0] == 0.0
    assert sorted(m.sample_times) == m.sample_times
