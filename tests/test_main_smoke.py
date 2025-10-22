import sys

from procsight.models.metrics import (
    ContextSwitchesUsage,
    CpuUsage,
    DescriptorUsage,
    IOUsage,
    MemoryUsage,
    ProcessMeta,
    ProcessSample,
    ThreadUsage,
)


class _FakeMonitor:
    def __init__(self, pid: int, interval: float):
        self.sample_times = [0.0, 1.0]

    def get_process_usage_by_interval(self, duration, samples, extended=False):
        if extended:
            return [
                ProcessSample(
                    sample=1,
                    cpu=CpuUsage(process=10.0, user=1.0, system=0.5),
                    memory=MemoryUsage(rss=50.0, vms=70.0),
                    io=IOUsage(
                        read_count=1, write_count=1, read_bytes=100, write_bytes=200
                    ),
                    ctx=ContextSwitchesUsage(voluntary=1, involuntary=2),
                    descriptors=DescriptorUsage(open_files=1, fds=2),
                    threads=ThreadUsage(threads=2),
                    meta=ProcessMeta(pid=1, uptime_sec=1.0, status="running"),
                ),
                ProcessSample(
                    sample=2,
                    cpu=CpuUsage(process=20.0, user=2.0, system=1.0),
                    memory=MemoryUsage(rss=60.0, vms=80.0),
                    io=IOUsage(
                        read_count=2, write_count=2, read_bytes=200, write_bytes=400
                    ),
                    ctx=ContextSwitchesUsage(voluntary=2, involuntary=4),
                    descriptors=DescriptorUsage(open_files=2, fds=4),
                    threads=ThreadUsage(threads=3),
                    meta=ProcessMeta(pid=1, uptime_sec=2.0, status="running"),
                ),
            ]
        else:
            return [
                (CpuUsage(process=10.0), MemoryUsage(rss=50.0, vms=70.0)),
                (CpuUsage(process=20.0), MemoryUsage(rss=60.0, vms=80.0)),
            ]


def test_main_basic_flow(monkeypatch, tmp_path):
    import main as app

    # Patch Monitor inside main module
    monkeypatch.setattr(app, "Monitor", _FakeMonitor)

    # Avoid writing CSV and plots unless we direct to tmp
    plots_dir = tmp_path / "plots"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--pid",
            "123",
            "--samples",
            "2",
            "--no-show",
            "--save-plots",
            str(plots_dir),
            "--dpi",
            "72",
        ],
    )

    app.main()


def test_main_extended_flow(monkeypatch, tmp_path):
    import main as app

    # Patch Monitor inside main module
    monkeypatch.setattr(app, "Monitor", _FakeMonitor)

    plots_dir = tmp_path / "plots_ext"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--pid",
            "123",
            "--samples",
            "2",
            "--no-show",
            "--save-plots",
            str(plots_dir),
            "--extended",
            "--dpi",
            "72",
        ],
    )

    app.main()
