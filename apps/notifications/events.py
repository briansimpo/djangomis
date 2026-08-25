from dataclasses import dataclass
from djangospice.events import BaseEvent
from apps.notifications.models import Notification


@dataclass
class NotificationRecordCreated(BaseEvent):
    notification: Notification
    
