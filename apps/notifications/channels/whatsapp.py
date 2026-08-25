import logging
from typing import Any

from django.contrib.auth.models import AbstractUser

from apps.notifications.channels import NotificationChannel
from apps.notifications.enums import Channel
from apps.notifications.messages import WhatsAppMessage
from apps.notifications.models import Notification


logger = logging.getLogger(__name__)


class WhatsAppChannel(NotificationChannel[WhatsAppMessage]):
    """Delivers notifications via WhatsApp."""

    channel = Channel.WHATSAPP

    def send(self, user: AbstractUser, notification: Notification) -> dict[str, Any] | None:
        message = self.message(notification)
        phone = getattr(user, "phone_number", None)

        if not message or not phone:
            return None

        # TODO: Replace with Meta/WhatsApp Business API integration
        logger.info("WhatsApp %s -> %s", phone, message.body)
        return {"whatsapp": phone}
