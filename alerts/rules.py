from alerts.models import Alert


def evaluate_metrics(
    hostname: str,
    metrics: dict,
    config,
) -> list[Alert]:

    alerts = []

    cpu = metrics.get("cpu", {}).get("percent", 0)

    if cpu >= config.cpu_threshold:
        alerts.append(
            Alert(
                source=hostname,
                category="HIGH_CPU",
                severity="warning",
                message=(
                    f"CPU usage is {cpu:.1f}%"
                ),
                details={
                    "current": cpu,
                    "threshold": config.cpu_threshold,
                },
            )
        )

    memory = metrics.get("memory", {}).get("percent", 0)

    if memory >= config.memory_threshold:
        alerts.append(
            Alert(
                source=hostname,
                category="HIGH_MEMORY",
                severity="warning",
                message=(
                    f"Memory usage is {memory:.1f}%"
                ),
                details={
                    "current": memory,
                    "threshold": config.memory_threshold,
                },
            )
        )

    disks = metrics.get("disk", {})

    for mountpoint, disk in disks.items():
        usage = disk.get("percent", 0)

        if usage >= config.disk_threshold:
            alerts.append(
                Alert(
                    source=hostname,
                    category="HIGH_DISK",
                    severity="critical",
                    message=(
                        f"Disk usage on {mountpoint} "
                        f"is {usage:.1f}%"
                    ),
                    details={
                        "mountpoint": mountpoint,
                        "current": usage,
                        "threshold": config.disk_threshold,
                    },
                )
            )

    services = metrics.get("services", [])

    for service in services:
        status = service.get("status", "unknown")

        if status != "active":
            alerts.append(
                Alert(
                    source=hostname,
                    category="SERVICE_DOWN",
                    severity="critical",
                    message=(
                        f"Service {service.get('name')} "
                        f"status is {status}"
                    ),
                    details=service,
                )
            )

    return alerts


def evaluate_agent_status(
    hostname: str,
    last_seen_seconds: float,
    config,
) -> list[Alert]:

    if last_seen_seconds <= config.agent_timeout:
        return []

    return [
        Alert(
            source=hostname,
            category="AGENT_OFFLINE",
            severity="critical",
            message=(
                f"Agent has not reported for "
                f"{last_seen_seconds:.0f} seconds"
            ),
            details={
                "last_seen_seconds": last_seen_seconds,
                "timeout": config.agent_timeout,
            },
        )
    ]