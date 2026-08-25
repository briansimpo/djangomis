from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from djangospice.web.templates import get_template_name
from djangospice.apps.helpers import get_user_apps
from djangospice.htmx.views.generic import HTMXView
from djangospice.htmx.renderers import htmx_render
from apps.accounts.mixins import StaffLoginRequired
from apps.calendar.helpers import get_requested_calendar_period_id, get_open_calendar_period, clear_session_calendar_period_id, set_session_calendar_period_id
from apps.organization.helpers import get_requested_org_unit_id, clear_session_org_unit_id, set_session_org_unit_id
from .helpers import user_belongs_to_org_unit
from .apps import app_name


class HomeView(StaffLoginRequired, TemplateView):
    template_name = get_template_name("home.html", app_name)
    

class BaseSwitchView(StaffLoginRequired, FormView):
    default_redirect_url = "workspace:home"

    def redirect_back(self):
        referer = self.request.META.get("HTTP_REFERER")
        return redirect(referer or reverse(self.default_redirect_url))
       

class SwitchOrgUnitView(BaseSwitchView):
    def post(self, request, *args, **kwargs):
        org_unit_id = get_requested_org_unit_id(request)

        # 1. Clear Selection
        if not org_unit_id:
            clear_session_org_unit_id(request)
            clear_session_calendar_period_id(request)
            return self.redirect_back()

        # 2. Security / Tenant Isolation
        has_access = request.user.is_superuser or user_belongs_to_org_unit(request.user, org_unit_id)

        if not has_access:
            messages.error(request, "Access denied for this organizational unit.")
            return self.redirect_back()

        # 3. Apply Selection (Stored as Strings!)
        set_session_org_unit_id(request, str(org_unit_id))

        # 4. Cascade active period resolution
        calendar_period = get_open_calendar_period(org_unit_id)
        if calendar_period:
            set_session_calendar_period_id(request, str(calendar_period.id))  
        else:
            clear_session_calendar_period_id(request)
            
        messages.success(request, "Workspace updated.")
        return self.redirect_back()


class SwitchPeriodView(BaseSwitchView):
    def post(self, request, *args, **kwargs):
        calendar_period_id = get_requested_calendar_period_id(request)

        if calendar_period_id:
            set_session_calendar_period_id(request, str(calendar_period_id))  
            messages.success(request, "Period updated.")
        else:
            clear_session_calendar_period_id(request)
            messages.success(request, "Switched to all periods.")
            
        return self.redirect_back()

  
class UserAppsView(HTMXView):
    htmx_template_name = get_template_name("htmx/apps.html", app_name)

    def get(self, request, *args, **kwargs):
        """
        Normal page load
        """
        apps = get_user_apps(request)
        return htmx_render(request, self.htmx_template_name, {
            "apps": apps
        })

    def post(self, request, *args, **kwargs):
        """
        HTMX filtering
        """
        q = request.POST.get("q", "").strip()
        apps = get_user_apps(request)

        if q:
            apps = apps.filter(verbose_name__icontains=q)

        return htmx_render(
            request,
            self.htmx_template_name,
            {"apps": apps}
        )
