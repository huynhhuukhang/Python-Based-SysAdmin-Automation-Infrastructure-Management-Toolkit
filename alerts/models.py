from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class Alert:
    source: str
    category: str
    severity: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    alert_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "source": self.source,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "created_at": self.created_at,
        }

    def format_message(self) -> str:
        return (
            f"[{self.severity.upper()}] "
            f"{self.category}: {self.message}\n"
            f"Host: {self.source}\n"
            f"Time: {self.created_at}"
        )