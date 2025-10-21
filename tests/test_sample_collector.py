from time import time
from types import SimpleNamespace

import psutil
import pytest

from src.core.sample_collector import collect_basic_tuple, collect_sample


class FakeProc:
    def __init__(self):
        self._cpu_pct_calls = 0
        self.pid = 4242
        self._create_time = time() - 10.0

    # psutil.Process API subset
    def cpu_percent(self, interval=None):
        # Simulate stable CPU percent across calls
        self._cpu_pct_calls += 1
        return 200.0  # total across all cores

    def cpu_times(self):
        return SimpleNamespace(user=4.0, system=1.0)

    def memory_full_info(self):
        return SimpleNamespace(
            rss=200 * 1024**2,
            vms=300 * 1024**2,
            shared=10 * 1024**2,
            data=5 * 1024**2,
            text=2 * 1024**2,
        )

    def memory_info(self):
        return SimpleNamespace(rss=200 * 1024**2, vms=300 * 1024**2)

    def io_counters(self):
        return SimpleNamespace(
            read_count=1,
            write_count=2,
            read_bytes=1024,
            write_bytes=2048,
            read_chars=10,
            write_chars=20,
        )

    def num_ctx_switches(self):
        return SimpleNamespace(voluntary=3, involuntary=4)

    def open_files(self):
        return ["/tmp/file1"]

    def num_fds(self):
        return 8

    def num_threads(self):
        return 5

    def create_time(self):
        return self._create_time

    def status(self):
        return "running"

    def cpu_affinity(self):  # not available on macOS typically
        raise AttributeError("affinity not supported")


@pytest.fixture(autouse=True)
def _patch_cpu_count(monkeypatch):
    monkeypatch.setattr(psutil, "cpu_count", lambda logical=True: 4)


def test_collect_basic_tuple_normalizes_by_cores():
    proc = FakeProc()
    cpu, mem = collect_basic_tuple(proc)  # type: ignore[arg-type]

    # 200% total across 4 cores => per-core = 50%
    assert round(cpu.process, 2) == 50.00
    # rss/vms converted to MB
    assert mem.rss == pytest.approx(200.0, rel=0.0, abs=0.01)
    assert mem.vms == pytest.approx(300.0, rel=0.0, abs=0.01)


def test_collect_sample_full_payload():
    proc = FakeProc()
    # prime like Monitor does
    proc.cpu_percent(interval=None)

    sample = collect_sample(proc, sample_index=1)  # type: ignore[arg-type]

    assert sample.sample == 1
    assert sample.cpu.process == pytest.approx(50.0, abs=0.01)
    assert sample.memory.rss == pytest.approx(200.0, abs=0.01)
    assert sample.io.read_bytes == 1024
    assert sample.ctx.involuntary == 4
    assert sample.descriptors.open_files == 1
    assert sample.threads.threads == 5
    assert sample.meta.pid == 4242
    assert sample.meta.status == "running"
