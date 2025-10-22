from types import SimpleNamespace

import pandas as pd

from procsight.core.file_export import export_to_csv
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


def _mk_sample(i: int) -> ProcessSample:
    return ProcessSample(
        sample=i,
        cpu=CpuUsage(process=10.0 + i, user=1.0, system=0.5),
        memory=MemoryUsage(rss=50.0 + i, vms=75.0 + i, shared=1.0),
        io=IOUsage(
            read_count=i, write_count=i, read_bytes=100 * i, write_bytes=200 * i
        ),
        ctx=ContextSwitchesUsage(voluntary=i, involuntary=2 * i),
        descriptors=DescriptorUsage(open_files=i, fds=2 * i),
        threads=ThreadUsage(threads=1 + i),
        meta=ProcessMeta(
            pid=123, uptime_sec=float(i), status="running", cpu_affinity=[0, 1]
        ),
    )


def test_export_basic(tmp_path):
    args = SimpleNamespace(extended=False, out=str(tmp_path / "basic.csv"))
    data = [
        (CpuUsage(process=10.0), MemoryUsage(rss=50.0, vms=70.0)),
        (CpuUsage(process=20.0), MemoryUsage(rss=60.0, vms=80.0)),
    ]

    export_to_csv(args, data)

    df = pd.read_csv(args.out)
    # Expect 3 rows: two samples + avg row
    assert len(df) == 3
    assert set(["sample", "cpu_percent", "rss_mb", "vms_mb"]).issubset(df.columns)
    assert df.iloc[-1]["sample"] == "avg"


def test_export_extended(tmp_path):
    args = SimpleNamespace(extended=True, out=str(tmp_path / "ext.csv"))
    data = [_mk_sample(1), _mk_sample(2)]

    export_to_csv(args, data)

    df = pd.read_csv(args.out)
    # Expect 3 rows: two samples + avg row
    assert len(df) == 3
    # Check a few expected columns exist after normalization
    expected = {"sample", "cpu_percent", "rss_mb", "vms_mb", "uptime_sec", "status"}
    assert expected.issubset(set(df.columns))
