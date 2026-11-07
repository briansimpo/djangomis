from django.shortcuts import get_object_or_404
from djangospice.widget import Widget
from djangospice.widget.decorators import widget
from djangospice.core.decorators import get, post
from djangospice.utils import get_template_name
from djangospice.notification.helpers import notification_read, notification_read_all
from djangospice.apps.access import AppAccess
from .services import WorkspaceContextService
from .forms import WorkspaceContextForm
from .apps import namespace


@widget
class OrgContextWidget(Widget):
    template_name = get_template_name("widgets/org_context.html", namespace)
    login_required = True
    
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
    login_required = True
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
    def mark_all_as_read(self):
        unread_notifications = self.user.notifications.unread()
        for notification in unread_notifications:
            notification.mark_as_read()

        notification_read_all(self.user)
        return self.response().empty()

    @post
    def mark_as_read(self):
        notification = get_object_or_404(
            self.user.notifications,
            id=self.request.GET.get("id"),
        )

        if notification.unread:
            notification.mark_as_read()

        notification_read(notification)
        return self.response().empty()

      
@widget
class UserProfileWidget(Widget):
    template_name = get_template_name("widgets/user_profile.html", namespace)
    login_required = True


@widget
class AppLauncherWidget(Widget):
    template_name = get_template_name("widgets/app_launcher.html", namespace)
    partial_template = get_template_name("partials/app_grid.html", namespace)
    login_required = True

    
    def get_apps(self):
        app_access = AppAccess(self.user)
        return app_access.all()

    @get
    def load_apps(self):
        apps =  self.get_apps()
        context = {"apps": apps}
        return self.response().render(self.partial_template, context)

    @post
    def search_apps(self):
        q = self.request.POST.get("q", "").strip()
        apps = self.get_apps()
        if q:
            apps = apps.filter(name__icontains=q)
        context = {"apps": apps}
        return self.response().render(self.partial_template, context)
        
        
 