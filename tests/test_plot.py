from pathlib import Path

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
from procsight.visualization.plot import (
    plot_cpu_usage,
    plot_from_extended,
    plot_memory_usage,
)


def _samples() -> list[ProcessSample]:
    return [
        ProcessSample(
            sample=i,
            cpu=CpuUsage(process=10.0 + i, user=1.0, system=0.5),
            memory=MemoryUsage(
                rss=50.0 + i, vms=70.0 + i, shared=1.0, data=0.5, text=0.25
            ),
            io=IOUsage(
                read_count=i, write_count=i, read_bytes=100 * i, write_bytes=200 * i
            ),
            ctx=ContextSwitchesUsage(voluntary=i, involuntary=2 * i),
            descriptors=DescriptorUsage(open_files=i, fds=2 * i),
            threads=ThreadUsage(threads=1 + i),
            meta=ProcessMeta(
                pid=1, uptime_sec=float(i), status="running", cpu_affinity=[0, 1]
            ),
        )
        for i in (1, 2, 3)
    ]


def test_basic_plots(tmp_path: Path):
    data = [
        (CpuUsage(process=10.0), MemoryUsage(rss=50.0, vms=70.0)),
        (CpuUsage(process=20.0), MemoryUsage(rss=60.0, vms=80.0)),
    ]
    times = [0.0, 1.0]

    cpu_path = tmp_path / "cpu.png"
    mem_path = tmp_path / "mem.png"
    plot_cpu_usage(data, times, show=False, save_path=str(cpu_path))
    plot_memory_usage(data, times, show=False, save_path=str(mem_path))

    assert cpu_path.exists()
    assert mem_path.exists()


def test_extended_plot_suite(tmp_path: Path):
    samples = _samples()
    times = [0.0, 1.0, 2.0]

    out_dir = tmp_path / "plots"
    out_dir.mkdir()

    plot_from_extended(samples, times, out_dir=str(out_dir), show=False, ext="png")

    expected = [
        "cpu_components.png",
        "memory_breakdown.png",
        "io_cumulative.png",
        "ctx_switches.png",
        "descriptors_threads.png",
        "distributions.png",
        "corr_heatmap.png",
    ]
    for name in expected:
        assert (out_dir / name).exists()
