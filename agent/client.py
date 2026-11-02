import logging
from urllib.parse import urljoin

import requests


class AgentClient:
    def __init__(
        self,
        server_url: str,
        metrics_path: str,
        token: str = "",
        verify_tls: bool = True,
    ):
        self.server_url = server_url.rstrip("/")
        self.metrics_path = metrics_path.lstrip("/")
        self.verify_tls = verify_tls

        self.session = requests.Session()

        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "SysAdmin-Agent/1.0",
        })

        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })

    def send_metrics(self, payload: dict) -> bool:
        endpoint = urljoin(
            self.server_url + "/",
            self.metrics_path
        )

        try:
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=10,
                verify=self.verify_tls,
            )

            response.raise_for_status()

            logging.info(
                "Metrics successfully sent. HTTP %s",
                response.status_code,
            )

            return True

        except requests.RequestException as error:
            logging.error(
                "Failed to send metrics: %s",
                error,
            )

            return False

    def close(self):
        self.session.close()