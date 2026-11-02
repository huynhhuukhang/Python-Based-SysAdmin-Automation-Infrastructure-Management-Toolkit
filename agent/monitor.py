import platform
import socket
import time
from datetime import datetime, timezone

import psutil


def collect_metrics() -> dict:
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    disk_usage = {}

    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            disk_usage[partition.mountpoint] = {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            }

        except (PermissionError, OSError):
            continue

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    network = psutil.net_io_counters()

    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "collected_at": datetime.now(timezone.utc).isoformat(),

        "cpu": {
            "percent": psutil.cpu_percent(interval=1),
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "load_average": (
                list(psutil.getloadavg())
                if hasattr(psutil, "getloadavg")
                else None
            ),
        },

        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
        },

        "swap": {
            "total": swap.total,
            "used": swap.used,
            "percent": swap.percent,
        },

        "disk": disk_usage,

        "network": {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
        },

        "uptime_seconds": uptime_seconds,
    }