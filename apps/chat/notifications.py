from djangospice.core.decorators import get
from djangospice.notification.decorators import actionable
from djangospice.notification.base import Notification
from djangospice.notification.messages import DatabaseMessage
from djangospice.notification.actions import PostAction
 

@actionable
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