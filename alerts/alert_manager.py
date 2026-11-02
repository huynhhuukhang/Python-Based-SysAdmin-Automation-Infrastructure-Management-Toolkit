import logging
import time
from collections.abc import Callable

from alerts.notifier import AlertNotifier
from alerts.rules import (
    evaluate_agent_status,
    evaluate_metrics,
)


class AlertManager:
    def __init__(self, config):
        self.config = config
        self.notifier = AlertNotifier(config)

        # Lưu thời điểm gửi gần nhất của từng loại cảnh báo.
        self.last_sent = {}

    def _should_send(self, alert) -> bool:
        key = (
            alert.source,
            alert.category,
            alert.details.get("mountpoint", ""),
            alert.details.get("name", ""),
        )

        now = time.monotonic()
        last_time = self.last_sent.get(key, 0)

        if (
            now - last_time
            < self.config.cooldown_seconds
        ):
            return False

        self.last_sent[key] = now
        return True

    def process_metrics(
        self,
        hostname: str,
        metrics: dict,
    ) -> list:

        alerts = evaluate_metrics(
            hostname,
            metrics,
            self.config,
        )

        sent_alerts = []

        for alert in alerts:
            if self._should_send(alert):
                self.notifier.send(alert)
                sent_alerts.append(alert)

        return sent_alerts

    def process_agent_status(
        self,
        hostname: str,
        last_seen_seconds: float,
    ) -> list:

        alerts = evaluate_agent_status(
            hostname,
            last_seen_seconds,
            self.config,
        )

        sent_alerts = []

        for alert in alerts:
            if self._should_send(alert):
                self.notifier.send(alert)
                sent_alerts.append(alert)

        return sent_alerts