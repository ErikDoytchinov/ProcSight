from pydantic import BaseModel


class CpuUsage(BaseModel):
    percent: float


class MemoryUsage(BaseModel):
    rss: float
    vms: float
