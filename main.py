#!/usr/bin/env python3
import sys
from typing import List, Tuple

import psutil
from loguru import logger

from src.cli.parser import get_params
from src.core.file_export import export_to_csv
from src.core.monitor import Monitor
from src.models.metrics import CpuUsage, MemoryUsage
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

        export_to_csv(args, data)

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
