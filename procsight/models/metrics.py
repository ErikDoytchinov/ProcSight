from typing import List, Optional

from pydantic import BaseModel


class CpuUsage(BaseModel):
    process: float
    user: Optional[float] = None
    system: Optional[float] = None


class MemoryUsage(BaseModel):
    rss: float
    vms: float
    shared: Optional[float] = None
    data: Optional[float] = None
    text: Optional[float] = None


class IOUsage(BaseModel):
    read_count: int
    write_count: int
    read_bytes: int
    write_bytes: int
    read_chars: Optional[int] = None
    write_chars: Optional[int] = None


class ContextSwitchesUsage(BaseModel):
    voluntary: int
    involuntary: int


class DescriptorUsage(BaseModel):
    open_files: int
    fds: int


class ThreadUsage(BaseModel):
    threads: int


class ProcessMeta(BaseModel):
    pid: int
    uptime_sec: float
    status: str
    cpu_affinity: Optional[List[int]] = None


class ProcessSample(BaseModel):
    sample: int
    cpu: CpuUsage
    memory: MemoryUsage
    io: IOUsage
    ctx: ContextSwitchesUsage
    descriptors: DescriptorUsage
    threads: ThreadUsage
    meta: ProcessMeta
