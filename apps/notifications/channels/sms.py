import logging
from typing import Any

from django.contrib.auth.models import AbstractUser

from apps.notifications.channels import NotificationChannel
from apps.notifications.enums import Channel
from apps.notifications.messages import SmsMessage
from apps.notifications.models import Notification


logger = logging.getLogger(__name__)


class SMSChannel(NotificationChannel[SmsMessage]):
    """Delivers notifications via SMS."""

    channel = Channel.SMS

    def send(self, user: AbstractUser, notification: Notification) -> dict[str, Any] | None:
        message = self.message(notification)
        phone = getattr(user, "phone_number", None)

        if not message or not phone:
            return None

        # TODO: Replace with actual SMS provider integration (Twilio, AWS SNS, etc.)
        logger.info("SMS %s -> %s", phone, message.body)
        return {"phone": phone}

