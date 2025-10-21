#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import List, Tuple, cast

import psutil
from loguru import logger

from src.cli.parser import get_params
from src.core.file_export import export_to_csv
from src.core.monitor import Monitor
from src.models.metrics import CpuUsage, MemoryUsage, ProcessSample
from src.visualization.plot import (
    plot_cpu_usage,
    plot_from_extended,
    plot_memory_usage,
)


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
            export_to_csv(args, data)

        if not args.extended:
            basic_tuples: List[Tuple[CpuUsage, MemoryUsage]] = data  # type: ignore[assignment]
            for cpu_usage, memory_usage in basic_tuples:
                logger.debug(f"CPU:{cpu_usage.model_dump_json}")
                logger.debug(f"Memory:{memory_usage.model_dump_json}")

            # we use actual sampled times captured by Monitor
            times = monitor.sample_times

            cpu_path = None
            mem_path = None
            if args.save_plots:
                p = Path(args.save_plots)
                p.mkdir(parents=True, exist_ok=True)
                ext = getattr(args, "img_format", "png")
                cpu_path = str(p / f"cpu_pid{args.pid}.{ext}")
                mem_path = str(p / f"mem_pid{args.pid}.{ext}")

            plot_cpu_usage(
                basic_tuples,
                times,
                show=not args.no_show,
                save_path=cpu_path,
                dpi=args.dpi,
                transparent=getattr(args, "transparent", False),
                theme=getattr(args, "theme", "light"),
            )
            plot_memory_usage(
                basic_tuples,
                times,
                show=not args.no_show,
                save_path=mem_path,
                dpi=args.dpi,
                transparent=getattr(args, "transparent", False),
                theme=getattr(args, "theme", "light"),
            )
        else:
            # extended mode: produce richer plots
            out_dir = None
            if args.save_plots:
                p = Path(args.save_plots)
                p.mkdir(parents=True, exist_ok=True)
                out_dir = str(p)

            samples_ext = cast(List[ProcessSample], data)
            times = monitor.sample_times
            plot_from_extended(
                samples_ext,
                times,
                out_dir=out_dir,
                show=not args.no_show,
                dpi=args.dpi,
                theme=getattr(args, "theme", "light"),
                ext=getattr(args, "img_format", "png"),
            )
    except psutil.NoSuchProcess:
        logger.error(f"process PID not found (pid={args.pid})")
    except ValueError as e:
        logger.error(f"There was an issue during execution: {e}")


if __name__ == "__main__":
    main()
