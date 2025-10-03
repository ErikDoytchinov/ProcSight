#!/usr/bin/env python3
import sys

import psutil
from loguru import logger
from pandas import DataFrame

from src.cli.parser import get_params
from src.core.monitor import Monitor
from src.models.metrics import CpuUsage, MemoryUsage
from src.visualization.plot import plot_cpu_usage, plot_memory_usage

DURATION = 60


def main():
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    args = get_params()

    # init a monitor
    try:
        monitor = Monitor(pid=args.pid[0], interval=args.interval[0])

        # run monitor for some time
        data: list[tuple[CpuUsage, MemoryUsage]] = (
            monitor.get_process_usage_by_interval(
                duration=DURATION,
            )
        )

        if args.out:
            DataFrame(
                data={
                    "cpu_usage": [cpu[0] for cpu in data],
                    "memory_usage": [memory[1] for memory in data],
                }
            ).to_csv(args.out[0])
            logger.info(f"Saved a .csv file at: {args.out[0]}")

        # pass data to visualizer
        for cpu_usage, memory_usage in data:
            logger.debug(f"CPU:{cpu_usage.model_dump_json}")
            logger.debug(f"Memory:{memory_usage.model_dump_json}")

        interval = args.interval[0]
        times = [i * interval for i in range(len(data))]

        plot_cpu_usage(data, times)

        plot_memory_usage(data, times)
        # call some pre configured visualizer plots
        # store them in a folder on the computer
    except psutil.NoSuchProcess:
        logger.error(f"process PID not found (pid={args.pid[0]})")


if __name__ == "__main__":
    main()
