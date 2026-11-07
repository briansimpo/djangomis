from djangospice.exec.decorators import executable, get
from djangospice.notification.base import Notification
from djangospice.notification.messages import DatabaseMessage
from djangospice.htmx.shortcuts import response
 

@executable
class FriendRequest(Notification):
    login_required = True

    def to_database(self, user):
        return DatabaseMessage(
            title="New Friend Request",
            body="You have receieved a new friend request",     
        )

    @get
    def confirm(self):
        return response("Confirmed")

    @get
    def reject(self):
        return response("Rejected")