from django.shortcuts import get_object_or_404
from djangospice.widget import Widget
from djangospice.widget.decorators import widget, post
from djangospice.utils import get_template_name
from djangospice.notification.helpers import notification_read, notification_read_all
from .services import WorkspaceContextService
from .forms import WorkspaceContextForm
from .apps import namespace


@widget
class OrgContextWidget(Widget):
    template_name = get_template_name("widgets/org_context.html", namespace)
    
    def get_context(self):
        context = super().get_context()
        context["form"] = WorkspaceContextForm(request=self.request)
        return context

    def post(self):
        org_unit = self.request_value("org_unit")
        calendar_period = self.request_value("calendar_period")

        try:
            WorkspaceContextService.resolve_user_selection(
                request=self.request,
                user=self.user,
                org_unit_id=org_unit,
                calendar_period_id=calendar_period
            )
        except ValueError:
            return self.refresh_widget()

        return self.refresh_widget()


@widget
class NotificationWidget(Widget):
    template_name = get_template_name("widgets/notification.html", namespace)
    limit = 10

    def get_context(self):
        context = super().get_context()

        unread_count = self.user.notifications.unread().count()
        notifications =  self.user.notifications.order_by("-timestamp")[:self.limit]

        context.update({
            "unread_count": unread_count,
            "notifications": notifications,
        })

        return context

    @post
    def mark_all_as_read(self, request):
        unread_notifications = self.user.notifications.unread()
        for notification in unread_notifications:
            notification.mark_as_read()

        notification_read_all(request.user)
        return self.response().empty()

    @post
    def mark_as_read(self, request):
        notification = get_object_or_404(
            self.user.notifications,
            id=request.GET.get("id"),
        )

        if notification.unread:
            notification.mark_as_read()

        notification_read(notification)
        return self.response().empty()

      
@widget
class UserProfileWidget(Widget):
    template_name = get_template_name("widgets/user_profile.html", namespace)

