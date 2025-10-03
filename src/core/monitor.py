import time
from datetime import datetime, timedelta

import psutil
import schedule
from loguru import logger

from src.models.metrics import CpuUsage, MemoryUsage


class Monitor:
    def __init__(self, pid: int, interval: int):
        self.pid = pid
        self.interval = interval

    def get_process_usage_by_interval(
        self, duration: int
    ) -> list[tuple[CpuUsage, MemoryUsage]]:
        collection: list[tuple[CpuUsage, MemoryUsage]] = list()

        self.__get_all_usage_metrics(collection)

        schedule.clear()
        schedule.every(self.interval).seconds.do(
            self.__get_all_usage_metrics, collection
        )

        end_time = datetime.now() + timedelta(seconds=duration)
        while datetime.now() < end_time:
            schedule.run_pending()
            time.sleep(0.1)

        schedule.clear()
        return collection

    def __get_all_usage_metrics(
        self, collection: list[tuple[CpuUsage, MemoryUsage]]
    ) -> None:
        cpu_usage = self.__get_cpu_usage(self.pid)
        memory_usage = self.__get_memory_usage(self.pid)

        logger.debug(f"cpu: {cpu_usage.model_dump_json()}")
        logger.debug(f"memory: {memory_usage.model_dump_json()}")

        collection.append((cpu_usage, memory_usage))

    def __get_cpu_usage(self, pid: int) -> CpuUsage:
        return CpuUsage(percent=psutil.Process(pid=pid).cpu_percent(interval=1))

    def __get_memory_usage(self, pid: int) -> MemoryUsage:
        raw = psutil.Process(pid=pid).memory_info()._asdict()
        return MemoryUsage(
            rss=raw["rss"] / (1024**2),
            vms=raw["vms"] / (1024**2),
        )
