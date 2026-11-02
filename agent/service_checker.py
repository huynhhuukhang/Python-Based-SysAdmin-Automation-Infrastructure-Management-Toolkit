import re
import subprocess


SERVICE_PATTERN = re.compile(
    r"^[a-zA-Z0-9_.@:-]+\.service$"
)


def check_service(service_name: str) -> dict:
    if not SERVICE_PATTERN.match(service_name):
        return {
            "name": service_name,
            "status": "invalid",
            "error": "Invalid systemd service name",
        }

    try:
        result = subprocess.run(
            [
                "systemctl",
                "is-active",
                service_name,
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        status = result.stdout.strip()

        if not status:
            status = "unknown"

        return {
            "name": service_name,
            "status": status,
            "active": status == "active",
        }

    except FileNotFoundError:
        return {
            "name": service_name,
            "status": "unsupported",
            "error": "systemctl is not available",
        }

    except subprocess.TimeoutExpired:
        return {
            "name": service_name,
            "status": "timeout",
            "error": "Service check timed out",
        }


def check_services(service_names: list[str]) -> list[dict]:
    return [
        check_service(service)
        for service in service_names
    ]