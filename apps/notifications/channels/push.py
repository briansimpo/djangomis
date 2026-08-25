import logging
from typing import Any

from django.contrib.auth.models import AbstractUser

from apps.notifications.channels import NotificationChannel
from apps.notifications.enums import Channel
from apps.notifications.messages import PushMessage
from apps.notifications.models import Notification


logger = logging.getLogger(__name__)


class PushChannel(NotificationChannel[PushMessage]):
    """Delivers push notifications to mobile/web clients."""

    channel = Channel.PUSH

    def send(self, user: AbstractUser, notification: Notification) -> dict[str, Any] | None:
        message = self.message(notification)

        if not message:
            return None

        # TODO: Replace with actual FCM/APNS provider integration
        logger.info("Push -> user=%s title=%s", user.pk, message.title)
        return {"user": user.pk}

