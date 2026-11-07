from djangospice.exec.decorators import executable, get
from djangospice.notification.base import Notification
from djangospice.notification.messages import DatabaseMessage

 

@executable
class FriendRequest(Notification):

    def to_database(self, user):
        return DatabaseMessage(
            title="New Friend Request",
            body="You have receieved a new friend request",     
        )

    @get
    def confirm(self):
        pass

    @get
    def reject(self):
        pass