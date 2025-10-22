from __future__ import annotations

from time import time
from typing import Optional, Tuple

import psutil  # type: ignore
from loguru import logger

from procsight.models.metrics import (
    ContextSwitchesUsage,
    CpuUsage,
    DescriptorUsage,
    IOUsage,
    MemoryUsage,
    ProcessMeta,
    ProcessSample,
    ThreadUsage,
)

_MB = 1024**2


def _effective_core_count(proc: psutil.Process) -> int:
    # try process CPU affinity (not available on macOS and some platforms)
    try:
        affinity = proc.cpu_affinity()  # type: ignore[attr-defined]
        if isinstance(affinity, (list, tuple)) and len(affinity) > 0:
            return max(1, len(affinity))
    except Exception:
        pass

    logical = psutil.cpu_count(logical=True) or 1
    return max(1, int(logical))


def collect_sample(proc: psutil.Process, sample_index: int) -> ProcessSample:
    """
    Collect a single rich process sample.

    Assumes caller has already *primed* cpu_percent with interval=None exactly once
    for the process before the first invocation, so this call is non-blocking.
    """
    # cpu
    cpu_pct_total = proc.cpu_percent(interval=None)
    cores = _effective_core_count(proc)
    cpu_times = proc.cpu_times()
    cpu = CpuUsage(
        process=cpu_pct_total / float(cores),
        user=getattr(cpu_times, "user") / float(cores),
        system=getattr(cpu_times, "system") / float(cores),
    )

    # memory (prefer full info when available; fallback gracefully)
    try:
        mem_full = proc.memory_full_info()
    except Exception:
        mem_full = proc.memory_info()

    memory = MemoryUsage(
        rss=getattr(mem_full, "rss", 0) / _MB,
        vms=getattr(mem_full, "vms", 0) / _MB,
        shared=(getattr(mem_full, "shared", None) or 0) / _MB
        if getattr(mem_full, "shared", None) is not None
        else None,
        data=(getattr(mem_full, "data", None) or 0) / _MB
        if getattr(mem_full, "data", None) is not None
        else None,
        text=(getattr(mem_full, "text", None) or 0) / _MB
        if getattr(mem_full, "text", None) is not None
        else None,
    )

    # IO
    try:
        io_c = proc.io_counters()  # type: ignore[attr-defined]
        io_usage = IOUsage(
            read_count=io_c.read_count,
            write_count=io_c.write_count,
            read_bytes=io_c.read_bytes,
            write_bytes=io_c.write_bytes,
            read_chars=getattr(io_c, "read_chars", None),
            write_chars=getattr(io_c, "write_chars", None),
        )
    except Exception:
        io_usage = IOUsage(
            read_count=0,
            write_count=0,
            read_bytes=0,
            write_bytes=0,
        )

    # ctx switch
    try:
        ctx = proc.num_ctx_switches()
        ctx_usage = ContextSwitchesUsage(
            voluntary=ctx.voluntary, involuntary=ctx.involuntary
        )
    except Exception:
        ctx_usage = ContextSwitchesUsage(voluntary=0, involuntary=0)

    # open files
    try:
        open_files = len(proc.open_files())
    except Exception:
        open_files = 0
    try:
        fds = proc.num_fds()
    except Exception:
        fds = 0
    desc_usage = DescriptorUsage(open_files=open_files, fds=fds)

    # threads
    try:
        thread_usage = ThreadUsage(threads=proc.num_threads())
    except Exception:
        thread_usage = ThreadUsage(threads=0)

    # meta
    now = time()
    try:
        create_time = proc.create_time()
        uptime = max(0.0, now - create_time)
    except Exception:
        uptime = 0.0
    try:
        status = proc.status()
    except Exception:
        status = "unknown"
    try:
        affinity = proc.cpu_affinity()  # type: ignore[attr-defined]
    except Exception:
        affinity = None
    meta = ProcessMeta(
        pid=proc.pid,
        uptime_sec=uptime,
        status=status,
        cpu_affinity=affinity,
    )

    sample = ProcessSample(
        sample=sample_index,
        cpu=cpu,
        memory=memory,
        io=io_usage,
        ctx=ctx_usage,
        descriptors=desc_usage,
        threads=thread_usage,
        meta=meta,
    )

    logger.debug(sample.model_dump_json())
    return sample


def collect_basic_tuple(
    proc: psutil.Process, precomputed_cpu_pct: Optional[float] = None
) -> Tuple[CpuUsage, MemoryUsage]:
    # total CPU% from psutil can be up to 100 * cores; normalize to per-core %
    cpu_pct_total = (
        precomputed_cpu_pct
        if precomputed_cpu_pct is not None
        else proc.cpu_percent(interval=None)
    )
    cores = _effective_core_count(proc)
    cpu_times = None
    cpu_times = proc.cpu_times()
    cpu = CpuUsage(
        process=cpu_pct_total / float(cores),
        user=getattr(cpu_times, "user") / float(cores),
        system=getattr(cpu_times, "system") / float(cores),
    )
    mem_info = proc.memory_info()
    memory = MemoryUsage(
        rss=mem_info.rss / _MB,
        vms=mem_info.vms / _MB,
    )
    return cpu, memory
