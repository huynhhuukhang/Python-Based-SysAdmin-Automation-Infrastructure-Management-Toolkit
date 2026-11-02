import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AlertConfig:
    cpu_threshold: float
    memory_threshold: float
    disk_threshold: float
    agent_timeout: int
    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str
    cooldown_seconds: int


def load_alert_config(path: str) -> AlertConfig:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Alert config not found: {path}"
        )

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    thresholds = data.get("thresholds", {})
    telegram = data.get("telegram", {})

    config = AlertConfig(
        cpu_threshold=float(
            thresholds.get("cpu_percent", 85)
        ),
        memory_threshold=float(
            thresholds.get("memory_percent", 90)
        ),
        disk_threshold=float(
            thresholds.get("disk_percent", 90)
        ),
        agent_timeout=int(
            thresholds.get("agent_timeout_seconds", 120)
        ),
        telegram_enabled=bool(
            telegram.get("enabled", False)
        ),
        telegram_bot_token=os.getenv(
            "TELEGRAM_BOT_TOKEN",
            telegram.get("bot_token", "")
        ),
        telegram_chat_id=os.getenv(
            "TELEGRAM_CHAT_ID",
            telegram.get("chat_id", "")
        ),
        cooldown_seconds=int(
            data.get("cooldown_seconds", 300)
        ),
    )

    for name, value in (
        ("CPU", config.cpu_threshold),
        ("Memory", config.memory_threshold),
        ("Disk", config.disk_threshold),
    ):
        if not 0 < value <= 100:
            raise ValueError(
                f"{name} threshold must be between 0 and 100"
            )

    if config.agent_timeout <= 0:
        raise ValueError("agent_timeout must be positive")

    if config.cooldown_seconds < 0:
        raise ValueError("cooldown_seconds cannot be negative")

    return config