from djangospice.notification.base import BaseNotification
from djangospice.notification.messages import DatabaseMessage
from djangospice.notification.metadata import  Action


class ChatNotification(BaseNotification):

    def to_database(self, user):
        return DatabaseMessage(
            title="New Message",
            body="You have receieved a new message",
            url="#",
            actions=[
                Action(label="Confirm", url="#"),
                Action(label="Reply", url="#"),
            ],
        )



