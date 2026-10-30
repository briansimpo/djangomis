from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from djangospice.widget import Widget, widget
from djangospice.templates import get_template_name

from .services import WorkspaceContextService
from .forms import WorkspaceContextForm
from .apps import namespace


@widget
class WorkspaceContext(Widget):
    template_name = get_template_name("widgets/context.html", namespace)
    redirect_url = "workspace:home"

    def get_context(self):
        context = super().get_context()
        context["form"] = WorkspaceContextForm(request=self.request)
        return context

    def redirect_back(self):
        referer = self.request.META.get("HTTP_REFERER")
        return redirect(referer or reverse(self.redirect_url))

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
            return self.redirect_back()

        return self.redirect_back()

