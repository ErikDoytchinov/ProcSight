from time import monotonic, sleep
from typing import List, Tuple

import psutil

from src.models.metrics import CpuUsage, MemoryUsage


class Monitor:
    def __init__(self, pid: int, interval: int):
        self.pid = pid
        self.interval = interval

    def get_process_usage_by_interval(
        self, duration: int, samples: int
    ) -> List[Tuple[CpuUsage, MemoryUsage]]:
        """Collect process metrics.

        Modes (mutually exclusive):
          - duration > 0: run for that many seconds
          - samples > 0: collect exactly N samples
          - neither: run until user interrupts with Ctrl+C (continuous)
        """
        if duration and samples:
            raise ValueError(
                "Provide only one of duration or samples (or neither for continuous mode)."
            )

        collection: List[Tuple[CpuUsage, MemoryUsage]] = []

        # prime CPU percent (first call always returns 0.0 otherwise)
        psutil.Process(self.pid).cpu_percent(interval=None)

        if duration:
            self.__collect_for_duration(duration, collection)
        elif samples:
            self.__collect_for_samples(samples, collection)
        else:
            self.__collect_continuous(collection)

        return collection

    def __collect_for_duration(
        self, duration: int, collection: List[Tuple[CpuUsage, MemoryUsage]]
    ) -> None:
        start = monotonic()
        interval = self.interval
        count = 0
        while (monotonic() - start) < duration:
            self.__get_all_usage_metrics(collection)
            count += 1
            next_time = start + count * interval
            sleep(max(0.0, next_time - monotonic()))

    def __collect_for_samples(
        self, samples: int, collection: List[Tuple[CpuUsage, MemoryUsage]]
    ) -> None:
        for _ in range(samples):
            self.__get_all_usage_metrics(collection)
            sleep(self.interval)

    def __collect_continuous(
        self, collection: List[Tuple[CpuUsage, MemoryUsage]]
    ) -> None:
        print("Sampling continuously. Press Ctrl+C to stop.")
        try:
            while True:
                self.__get_all_usage_metrics(collection)
                sleep(self.interval)
        except KeyboardInterrupt:
            print("\nStopping continuous sampling (Ctrl+C).")

    def __get_all_usage_metrics(
        self, collection: List[Tuple[CpuUsage, MemoryUsage]]
    ) -> None:
        cpu_usage = self.__get_cpu_usage(self.pid)
        memory_usage = self.__get_memory_usage(self.pid)
        collection.append((cpu_usage, memory_usage))

    def __get_cpu_usage(self, pid: int) -> CpuUsage:
        return CpuUsage(percent=psutil.Process(pid=pid).cpu_percent(interval=None))

    def __get_memory_usage(self, pid: int) -> MemoryUsage:
        raw = psutil.Process(pid=pid).memory_info()._asdict()
        return MemoryUsage(
            rss=raw["rss"] / (1024**2),
            vms=raw["vms"] / (1024**2),
        )
