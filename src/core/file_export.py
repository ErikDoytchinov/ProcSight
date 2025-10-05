from loguru import logger
from pandas import DataFrame

from src.models.metrics import CpuUsage, MemoryUsage, ProcessSample


def export_to_csv(args, data):
    if args.out:
        if args.extended:
            rows = []
            for s in data:
                assert isinstance(s, ProcessSample)
                rows.append(
                    {
                        "pid": s.meta.pid,
                        "uptime_sec": s.meta.uptime_sec,
                        "status": s.meta.status,
                        "cpu_percent": s.cpu.percent,
                        "cpu_user": s.cpu.user,
                        "cpu_system": s.cpu.system,
                        "rss_mb": s.memory.rss,
                        "vms_mb": s.memory.vms,
                        "shared_mb": s.memory.shared,
                        "data_mb": s.memory.data,
                        "text_mb": s.memory.text,
                        "read_count": s.io.read_count,
                        "write_count": s.io.write_count,
                        "read_bytes": s.io.read_bytes,
                        "write_bytes": s.io.write_bytes,
                        "read_chars": s.io.read_chars,
                        "write_chars": s.io.write_chars,
                        "ctx_voluntary": s.ctx.voluntary,
                        "ctx_involuntary": s.ctx.involuntary,
                        "open_files": s.descriptors.open_files,
                        "fds": s.descriptors.fds,
                        "threads": s.threads.threads,
                        "cpu_affinity": ";".join(map(str, s.meta.cpu_affinity))
                        if s.meta.cpu_affinity
                        else None,
                    }
                )
            DataFrame(rows).to_csv(args.out, index=False)
        else:
            basic_tuples: list[tuple[CpuUsage, MemoryUsage]] = data  # type: ignore[assignment]
            basic_rows = {
                "cpu_percent": [cpu.percent for cpu, _ in basic_tuples],
                "rss_mb": [mem.rss for _, mem in basic_tuples],
                "vms_mb": [mem.vms for _, mem in basic_tuples],
            }
            DataFrame(basic_rows).to_csv(args.out, index=False)
        logger.info(f"Saved CSV at: {args.out}")
