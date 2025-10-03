#!/usr/bin/env python3
import sys

import psutil
from loguru import logger
from pandas import DataFrame

from src.cli.parser import get_params
from src.core.monitor import Monitor
from src.models.metrics import CpuUsage, MemoryUsage
from src.visualization.plot import plot_cpu_usage, plot_memory_usage


def main():
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    args = get_params()

    # init a monitor
    try:
        monitor = Monitor(pid=args.pid, interval=args.interval)

        # run monitor for some time
        data: list[tuple[CpuUsage, MemoryUsage]] = (
            monitor.get_process_usage_by_interval(
                duration=args.duration, samples=args.samples
            )
        )

        if args.out:
            DataFrame(
                data={
                    "cpu_usage": [cpu[0] for cpu in data],
                    "memory_usage": [memory[1] for memory in data],
                }
            ).to_csv(args.out)
            logger.info(f"Saved a .csv file at: {args.out}")

        # pass data to visualizer
        for cpu_usage, memory_usage in data:
            logger.debug(f"CPU:{cpu_usage.model_dump_json}")
            logger.debug(f"Memory:{memory_usage.model_dump_json}")

        interval = args.interval
        times = [i * interval for i in range(len(data))]

        plot_cpu_usage(data, times)

        plot_memory_usage(data, times)
        # call some pre configured visualizer plots
        # store them in a folder on the computer
    except psutil.NoSuchProcess:
        logger.error(f"process PID not found (pid={args.pid})")
    except ValueError as e:
        logger.error(f"There was an issue during execution: {e}")


if __name__ == "__main__":
    main()
