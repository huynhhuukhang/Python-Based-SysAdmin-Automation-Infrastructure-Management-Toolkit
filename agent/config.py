import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AgentConfig:
    agent_name: str
    server_url: str
    agent_token: str
    interval: int
    metrics_path: str
    verify_tls: bool
    services: list[str]
    log_dir: str


def load_config(config_path: str) -> AgentConfig:
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with path.open("r", encoding="utf-8") as file:
        data: dict[str, Any] = yaml.safe_load(file) or {}

    agent_name = os.getenv(
        "SYSADMIN_AGENT_NAME",
        data.get("agent_name", socket.gethostname())
    )

    server_url = os.getenv(
        "SYSADMIN_SERVER_URL",
        data.get("server_url", "")
    )

    agent_token = os.getenv(
        "SYSADMIN_AGENT_TOKEN",
        data.get("agent_token", "")
    )

    interval = int(os.getenv(
        "SYSADMIN_AGENT_INTERVAL",
        data.get("interval", 30)
    ))

    metrics_path = data.get(
        "metrics_path",
        "/api/agent/metrics"
    )

    verify_tls_env = os.getenv("SYSADMIN_VERIFY_TLS")

    if verify_tls_env is None:
        verify_tls = bool(data.get("verify_tls", True))
    else:
        verify_tls = verify_tls_env.lower() in ("1", "true", "yes")

    services = data.get("services", ["ssh", "nginx"])
    log_dir = data.get("log_dir", "logs")

    if not server_url:
        raise ValueError("server_url is required")

    if interval < 5:
        raise ValueError("interval must be at least 5 seconds")

    if not metrics_path.startswith("/"):
        raise ValueError("metrics_path must start with '/'")

    return AgentConfig(
        agent_name=agent_name,
        server_url=server_url.rstrip("/"),
        agent_token=agent_token,
        interval=interval,
        metrics_path=metrics_path,
        verify_tls=verify_tls,
        services=services,
        log_dir=log_dir,
    )