import logging

from alerts.models import Alert
from alerts.telegram import TelegramNotifier


class AlertNotifier:
    def __init__(self, config):
        self.config = config

        self.telegram = TelegramNotifier(
            bot_token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
        )

    def send(self, alert: Alert):
        logging.warning(
            "ALERT: %s",
            alert.format_message(),
        )

        if self.config.telegram_enabled:
            self.telegram.send(alert.format_message())