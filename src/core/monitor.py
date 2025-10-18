from time import monotonic, sleep
from typing import List, Tuple, Union

import psutil

from src.core.sample_collector import collect_basic_tuple, collect_sample
from src.models.metrics import CpuUsage, MemoryUsage, ProcessSample


class Monitor:
    def __init__(self, pid: int, interval: int):
        self.pid = pid
        self.interval = interval
        self._sample_times: List[float] = []
        self._base_mono: float | None = None
        self._proc: psutil.Process = psutil.Process(self.pid)

    @property
    def sample_times(self) -> List[float]:
        """Return a list of elapsed seconds per collected sample (aligned to first sample)."""
        return list(self._sample_times)

    def get_process_usage_by_interval(
        self, duration: int, samples: int, extended: bool = False
    ) -> Union[List[Tuple[CpuUsage, MemoryUsage]], List[ProcessSample]]:
        """
        Collect process metrics.

        Modes (mutually exclusive):
          - duration > 0: run for that many seconds
          - samples > 0: collect exactly N samples
          - neither: run until user interrupts with Ctrl+C (continuous)
        """
        if duration and samples:
            raise ValueError(
                "Provide only one of duration or samples (or neither for continuous mode)."
            )

        # reset timing state for this run
        self._sample_times = []
        self._base_mono = None

        if extended:
            collection: Union[
                list[tuple[CpuUsage, MemoryUsage]], list[ProcessSample]
            ] = []
        else:
            collection = []

        if duration:
            self.__collect_for_duration(duration, collection, extended)
        elif samples:
            self.__collect_for_samples(samples, collection, extended)
        else:
            self.__collect_continuous(collection, extended)

        return collection

    def __collect_for_duration(self, duration: int, collection, extended: bool) -> None:
        start = monotonic()
        interval = self.interval
        count = 0
        while (monotonic() - start) < duration:
            self.__get_all_usage_metrics(collection, extended, sample_index=count + 1)
            count += 1
            next_time = start + count * interval
            sleep(max(0.0, next_time - monotonic()))

    def __collect_for_samples(self, samples: int, collection, extended: bool) -> None:
        for i in range(1, samples + 1):
            self.__get_all_usage_metrics(collection, extended, sample_index=i)
            sleep(self.interval)

    def __collect_continuous(self, collection, extended: bool) -> None:
        print("Sampling continuously. Press Ctrl+C to stop.")
        try:
            count = 0
            while True:
                count += 1
                self.__get_all_usage_metrics(collection, extended, sample_index=count)
                sleep(self.interval)
        except KeyboardInterrupt:
            print("\nStopping continuous sampling (Ctrl+C).")

    def __get_all_usage_metrics(
        self, collection, extended: bool, sample_index: int
    ) -> None:
        self._proc.cpu_percent(interval=None)

        now_m = monotonic()
        if self._base_mono is None:
            self._base_mono = now_m
        self._sample_times.append(now_m - self._base_mono)
        if extended:
            sample = collect_sample(self._proc, sample_index)
            collection.append(sample)
        else:
            cpu_usage, memory_usage = collect_basic_tuple(self._proc)
            collection.append((cpu_usage, memory_usage))
