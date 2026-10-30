from djangospice.notification.base import BaseNotification
from djangospice.notification.messages import DatabaseMessage


class ChatNotification(BaseNotification):

    def to_database(self, user):
        return DatabaseMessage(
            title="New Message",
            body="You have receieved a new message"
        )