import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from alerts.alert_manager import AlertManager
from alerts.config import load_alert_config

from sysadmin_toolkit.api.database import (
    get_db,
    save_alert,
    save_metrics,
    upsert_agent,
)
from sysadmin_toolkit.api.schemas.agent import AgentMetrics
from sysadmin_toolkit.api.security import verify_agent_token


router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"],
    dependencies=[Depends(verify_agent_token)],
)


def create_alert_manager():
    config_path = os.getenv(
        "SYSADMIN_ALERT_CONFIG",
        "alerts/alerts.example.yaml",
    )

    config = load_alert_config(config_path)

    return AlertManager(config)


alert_manager = create_alert_manager()


@router.post("/metrics")
def receive_metrics(data: AgentMetrics):
    """
    Receive monitoring metrics from a Linux Agent.
    """

    try:
        payload = data.model_dump(mode="json")

        received_at = datetime.now(
            timezone.utc
        ).isoformat()

        collected_at = data.collected_at.isoformat()

        with get_db() as conn:
            agent_id = upsert_agent(
                conn=conn,
                agent_name=data.agent,
                hostname=data.hostname,
                platform=data.platform,
                timestamp=received_at,
            )

            save_metrics(
                conn=conn,
                agent_id=agent_id,
                collected_at=collected_at,
                received_at=received_at,
                payload=payload,
            )

        # Evaluate alert rules after the metrics are stored.
        detected_alerts = alert_manager.process_metrics(
            hostname=data.hostname,
            metrics=payload,
        )

        if detected_alerts:
            with get_db() as conn:
                for alert in detected_alerts:
                    save_alert(conn, alert)

        return {
            "success": True,
            "message": "Metrics received successfully",
            "hostname": data.hostname,
            "alerts_detected": len(detected_alerts),
            "received_at": received_at,
        }

    except Exception:
        logging.exception(
            "Failed to process metrics from %s",
            data.hostname,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process agent metrics",
        )