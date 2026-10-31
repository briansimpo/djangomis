from django.views.generic import TemplateView
from djangospice.utils import get_template_name
from djangospice.htmx.views.generic import HTMXView
from djangospice.htmx.shortcuts import htmx_render
from accounts.mixins import StaffLoginRequired
from djangospice.apps.access import AppAccess
from .apps import namespace


class HomeView(StaffLoginRequired, TemplateView):
    template_name = get_template_name("home.html", namespace)
    

class GetAppsView(HTMXView):
    htmx_template_name = get_template_name("partials/apps.html", namespace)

    def get(self, request, *args, **kwargs):
        """
        Normal page load
        """

        app_access = AppAccess(request.user)
        apps = app_access.all()
        return htmx_render(request, self.htmx_template_name, {
            "apps": apps
        })

    def post(self, request, *args, **kwargs):
        """
        HTMX filtering
        """
        q = request.POST.get("q", "").strip()
        app_access = AppAccess(request.user)
        apps = app_access.all()

        if q:
            apps = apps.filter(name__icontains=q)

        return htmx_render(request, self.htmx_template_name, {
            "apps": apps
        })
