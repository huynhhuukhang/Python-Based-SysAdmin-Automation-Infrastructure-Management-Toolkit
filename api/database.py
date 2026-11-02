import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DATABASE_PATH = os.getenv(
    "SYSADMIN_DATABASE_PATH",
    "data/sysadmin.db",
)


def get_connection():
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        str(db_path),
        timeout=10,
    )

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


@contextmanager
def get_db():
    conn = get_connection()

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def init_database():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                hostname TEXT NOT NULL UNIQUE,
                platform TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'online'
            );

            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                collected_at TEXT NOT NULL,
                received_at TEXT NOT NULL,
                payload TEXT NOT NULL,

                FOREIGN KEY (agent_id)
                    REFERENCES agents(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS
                idx_metrics_agent_time
            ON metrics(agent_id, collected_at DESC);

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL UNIQUE,
                hostname TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open'
            );

            CREATE INDEX IF NOT EXISTS
                idx_alerts_hostname_time
            ON alerts(hostname, created_at DESC);
        """)


def upsert_agent(
    conn,
    agent_name: str,
    hostname: str,
    platform: str | None,
    timestamp: str,
) -> int:
    conn.execute(
        """
        INSERT INTO agents (
            agent_name,
            hostname,
            platform,
            first_seen,
            last_seen,
            status
        )
        VALUES (?, ?, ?, ?, ?, 'online')

        ON CONFLICT(hostname)
        DO UPDATE SET
            agent_name = excluded.agent_name,
            platform = excluded.platform,
            last_seen = excluded.last_seen,
            status = 'online'
        """,
        (
            agent_name,
            hostname,
            platform,
            timestamp,
            timestamp,
        ),
    )

    row = conn.execute(
        "SELECT id FROM agents WHERE hostname = ?",
        (hostname,),
    ).fetchone()

    return int(row["id"])


def save_metrics(
    conn,
    agent_id: int,
    collected_at: str,
    received_at: str,
    payload: dict,
):
    conn.execute(
        """
        INSERT INTO metrics (
            agent_id,
            collected_at,
            received_at,
            payload
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            agent_id,
            collected_at,
            received_at,
            json.dumps(payload),
        ),
    )


def save_alert(conn, alert):
    conn.execute(
        """
        INSERT OR IGNORE INTO alerts (
            alert_id,
            hostname,
            category,
            severity,
            message,
            details,
            created_at,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
        """,
        (
            alert.alert_id,
            alert.source,
            alert.category,
            alert.severity,
            alert.message,
            json.dumps(alert.details),
            alert.created_at,
        ),
    )