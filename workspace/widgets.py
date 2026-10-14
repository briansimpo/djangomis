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
        form = WorkspaceContextForm(
            self.request.POST,
            request=self.request,
        )

        if not form.is_valid():
            return self.render(
                self.request,
                self.template_name,
                {"form": form},
            )

        org_unit = form.cleaned_data["org_unit"]
        calendar_period = form.cleaned_data["calendar_period"]

        try:
            WorkspaceContextService.resolve_user_selection(
                request=self.request,
                user=self.user,
                org_unit_id=org_unit.pk if org_unit else None,
                calendar_period_id=(
                    calendar_period.pk if calendar_period else None
                ),
            )
        except ValueError:
            return self.redirect_back()

        return self.redirect_back()

