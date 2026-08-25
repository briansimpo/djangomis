import logging
from typing import Any

from django.contrib.auth.models import AbstractUser

from apps.notifications.channels import NotificationChannel
from apps.notifications.enums import Channel
from apps.notifications.messages import SlackMessage
from apps.notifications.models import Notification


logger = logging.getLogger(__name__)


class SlackChannel(NotificationChannel[SlackMessage]):
    """Delivers notifications via Slack."""

    channel = Channel.SLACK

    def send(self, user: AbstractUser, notification: Notification) -> dict[str, Any] | None:
        message = self.message(notification)

        if not message:
            return None

        # TODO: Implement Slack Block Kit / Webhook integration
        logger.info("Slack -> user=%s", user.pk)
        return {"user": user.pk}

