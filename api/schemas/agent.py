from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CPUData(BaseModel):
    percent: float = Field(ge=0, le=100)
    logical_cores: int | None = None
    physical_cores: int | None = None
    load_average: list[float] | None = None


class MemoryData(BaseModel):
    total: int
    available: int
    used: int
    percent: float = Field(ge=0, le=100)


class SwapData(BaseModel):
    total: int
    used: int
    percent: float = Field(ge=0, le=100)


class DiskData(BaseModel):
    total: int
    used: int
    free: int
    percent: float = Field(ge=0, le=100)


class NetworkData(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


class ServiceData(BaseModel):
    name: str
    status: str
    active: bool | None = None


class AgentMetrics(BaseModel):
    agent: str
    hostname: str
    platform: str | None = None
    collected_at: datetime

    cpu: CPUData
    memory: MemoryData
    swap: SwapData

    disk: dict[str, DiskData]
    network: NetworkData

    uptime_seconds: int = Field(ge=0)
    services: list[ServiceData] = Field(default_factory=list)

    class Config:
        extra = "ignore"