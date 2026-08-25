import logging
from typing import Any

from django.contrib.auth.models import AbstractUser

from apps.notifications.channels import NotificationChannel
from apps.notifications.enums import Channel
from apps.notifications.messages import TelegramMessage
from apps.notifications.models import Notification


logger = logging.getLogger(__name__)


class TelegramChannel(NotificationChannel[TelegramMessage]):
    """Delivers notifications via Telegram Bot API."""

    channel = Channel.TELEGRAM

    def send(self, user: AbstractUser, notification: Notification) -> dict[str, Any] | None:
        message = self.message(notification)
        telegram_id = getattr(user, "telegram_id", None) # Assume user has a linked ID

        if not message or not telegram_id:
            return None

        # TODO: Implement Telegram bot integration
        logger.info("Telegram %s -> %s", telegram_id, message.text)
        return {"telegram_id": telegram_id}