import argparse
import logging
import signal
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from agent.client import AgentClient
from agent.config import load_config
from agent.monitor import collect_metrics
from agent.service_checker import check_services


running = True


def setup_logging(log_dir: str):
    Path(log_dir).mkdir(
        parents=True,
        exist_ok=True,
    )

    log_file = Path(log_dir) / "agent.log"

    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(message)s"
        ),
        handlers=[
            logging.StreamHandler(sys.stdout),
            handler,
        ],
    )


def handle_shutdown(signum, frame):
    global running

    logging.info(
        "Received shutdown signal: %s",
        signum,
    )

    running = False


def collect_agent_data(config) -> dict:
    metrics = collect_metrics()

    metrics["agent"] = config.agent_name

    metrics["services"] = check_services(
        config.services
    )

    return metrics


def run_agent(config, once: bool = False):
    client = AgentClient(
        server_url=config.server_url,
        metrics_path=config.metrics_path,
        token=config.agent_token,
        verify_tls=config.verify_tls,
    )

    logging.info(
        "Starting agent: %s",
        config.agent_name,
    )

    logging.info(
        "Server: %s",
        config.server_url,
    )

    try:
        while running:
            start_time = time.monotonic()

            try:
                payload = collect_agent_data(config)

                logging.info(
                    "Collected metrics from %s",
                    payload["hostname"],
                )

                client.send_metrics(payload)

            except Exception:
                logging.exception(
                    "Unexpected error during collection"
                )

            if once:
                break

            elapsed = time.monotonic() - start_time

            sleep_time = max(
                0,
                config.interval - elapsed,
            )

            time.sleep(sleep_time)

    finally:
        client.close()

        logging.info("Agent stopped")


def main():
    parser = argparse.ArgumentParser(
        description="SysAdmin Monitoring Agent"
    )

    parser.add_argument(
        "--config",
        default="agent.yaml",
        help="Path to agent YAML configuration",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Collect and send metrics only once",
    )

    args = parser.parse_args()

    try:
        config = load_config(args.config)

        setup_logging(config.log_dir)

        signal.signal(
            signal.SIGINT,
            handle_shutdown,
        )

        signal.signal(
            signal.SIGTERM,
            handle_shutdown,
        )

        run_agent(
            config,
            once=args.once,
        )

    except Exception as error:
        print(f"Agent startup failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()