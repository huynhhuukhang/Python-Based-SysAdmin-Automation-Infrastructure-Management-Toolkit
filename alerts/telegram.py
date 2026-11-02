import logging

import requests


class TelegramNotifier:
    API_URL = "https://api.telegram.org"

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
    ):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            logging.error(
                "Telegram bot token or chat ID is missing"
            )
            return False

        url = (
            f"{self.API_URL}/bot"
            f"{self.bot_token}/sendMessage"
        )

        try:
            response = requests.post(
                url,
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                },
                timeout=10,
            )

            response.raise_for_status()

            result = response.json()

            if not result.get("ok"):
                logging.error(
                    "Telegram API returned an unsuccessful response"
                )
                return False

            logging.info("Telegram alert sent successfully")

            return True

        except requests.RequestException as error:
            logging.error(
                "Failed to send Telegram alert: %s",
                error,
            )
            return False