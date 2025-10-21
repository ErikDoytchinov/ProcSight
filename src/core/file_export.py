import pandas as pd
from loguru import logger
from pandas import DataFrame

from src.models.metrics import CpuUsage, MemoryUsage


def _append_average_row(df: DataFrame) -> DataFrame:
    means = df.drop(columns=["sample"], errors="ignore").mean(numeric_only=True)
    avg_row = {"sample": "avg", **means.to_dict()}
    return pd.concat([df, DataFrame([avg_row])], ignore_index=True)


def export_to_csv(args, data):
    if args.extended:
        rows = [s.model_dump() for s in data]
        df = pd.json_normalize(rows)

        rename_map = {
            "sample": "sample",
            "meta.uptime_sec": "uptime_sec",
            "meta.status": "status",
            "cpu.process": "cpu_percent",
            "cpu.user": "cpu_user",
            "cpu.system": "cpu_system",
            "memory.rss": "rss_mb",
            "memory.vms": "vms_mb",
            "memory.shared": "shared_mb",
            "memory.data": "data_mb",
            "memory.text": "text_mb",
            "io.read_count": "read_count",
            "io.write_count": "write_count",
            "io.read_bytes": "read_bytes",
            "io.write_bytes": "write_bytes",
            "io.read_chars": "read_chars",
            "io.write_chars": "write_chars",
            "ctx.voluntary": "ctx_voluntary",
            "ctx.involuntary": "ctx_involuntary",
            "descriptors.open_files": "open_files",
            "descriptors.fds": "fds",
            "threads.threads": "threads",
            "meta.cpu_affinity": "cpu_affinity",
        }
        df = df.rename(columns=rename_map)

        if "cpu_affinity" in df.columns:

            def _join_affinity(v):
                if isinstance(v, (list, tuple)) and len(v) > 0:
                    return ";".join(map(str, v))
                return None

            df["cpu_affinity"] = df["cpu_affinity"].apply(_join_affinity)

        preferred_order = [
            "sample",
            "uptime_sec",
            "status",
            "cpu_percent",
            "cpu_user",
            "cpu_system",
            "rss_mb",
            "vms_mb",
            "shared_mb",
            "data_mb",
            "text_mb",
            "read_count",
            "write_count",
            "read_bytes",
            "write_bytes",
            "read_chars",
            "write_chars",
            "ctx_voluntary",
            "ctx_involuntary",
            "open_files",
            "fds",
            "threads",
            "cpu_affinity",
        ]
        existing_cols = [c for c in preferred_order if c in df.columns]
        df = df[existing_cols]

        df = _append_average_row(df)
        df.to_csv(args.out, index=False)
    else:
        basic_tuples: list[tuple[CpuUsage, MemoryUsage]] = data
        rows = [
            {
                "sample": i + 1,
                "cpu_percent": cpu.process,
                "rss_mb": mem.rss,
                "vms_mb": mem.vms,
            }
            for i, (cpu, mem) in enumerate(basic_tuples)
        ]
        df = DataFrame(rows)
        df = _append_average_row(df)
        df.to_csv(args.out, index=False)
    logger.info(f"Saved CSV at: {args.out}")
