#!/usr/bin/env python3
import sys
from typing import List, Tuple

import psutil
from loguru import logger
from pandas import DataFrame

from src.cli.parser import get_params
from src.core.monitor import Monitor
from src.models.metrics import CpuUsage, MemoryUsage, ProcessSample
from src.visualization.plot import plot_cpu_usage, plot_memory_usage


def main():
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    args = get_params()

    try:
        monitor = Monitor(pid=args.pid, interval=args.interval)

        data = monitor.get_process_usage_by_interval(
            duration=args.duration, samples=args.samples, extended=args.extended
        )

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
                basic_tuples: List[Tuple[CpuUsage, MemoryUsage]] = data  # type: ignore[assignment]
                basic_rows = {
                    "cpu_percent": [cpu.percent for cpu, _ in basic_tuples],
                    "rss_mb": [mem.rss for _, mem in basic_tuples],
                    "vms_mb": [mem.vms for _, mem in basic_tuples],
                }
                DataFrame(basic_rows).to_csv(args.out, index=False)
            logger.info(f"Saved CSV at: {args.out}")

        if not args.extended:
            basic_tuples: List[Tuple[CpuUsage, MemoryUsage]] = data  # type: ignore[assignment]
            for cpu_usage, memory_usage in basic_tuples:
                logger.debug(f"CPU:{cpu_usage.model_dump_json}")
                logger.debug(f"Memory:{memory_usage.model_dump_json}")

            interval = args.interval
            times = [i * interval for i in range(len(basic_tuples))]
            plot_cpu_usage(basic_tuples, times)
            plot_memory_usage(basic_tuples, times)
        else:
            logger.info(
                "Extended sampling complete (plots currently only for basic mode)."
            )
        # call some pre configured visualizer plots
        # store them in a folder on the computer
    except psutil.NoSuchProcess:
        logger.error(f"process PID not found (pid={args.pid})")
    except ValueError as e:
        logger.error(f"There was an issue during execution: {e}")


if __name__ == "__main__":
    main()
