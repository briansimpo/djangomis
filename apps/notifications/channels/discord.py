import logging
from typing import Any

from django.contrib.auth.models import AbstractUser

from apps.notifications.channels import NotificationChannel
from apps.notifications.enums import Channel
from apps.notifications.messages import DiscordMessage
from apps.notifications.models import Notification


logger = logging.getLogger(__name__)


class DiscordChannel(NotificationChannel[DiscordMessage]):
    """Delivers notifications via Discord Webhooks/Bot API."""

    channel = Channel.DISCORD

    def send(self, user: AbstractUser, notification: Notification) -> dict[str, Any] | None:
        message = self.message(notification)

        if not message:
            return None

        # TODO: Implement Discord webhook integration
        logger.info("Discord -> user=%s", user.pk)
        return {"user": user.pk}

