from django import forms

from djangospice.lookup.widget import LookupWidget

from apps.organization.models import OrgUnit
from apps.calendar.models import CalendarPeriod
from .services import WorkspaceContextService


class WorkspaceContextForm(forms.Form):
    org_unit = forms.ModelChoiceField(
        label="Organisation Unit",
        queryset=OrgUnit.objects.all(),
        required=True,
        widget=LookupWidget(
            model=OrgUnit,
            placeholder="Select organisation unit...",
            search_placeholder="Search organisation units...",
        ),
    )

    calendar_period = forms.ModelChoiceField(
        label="Calendar Period",
        queryset=CalendarPeriod.objects.all(),
        required=True,
        widget=LookupWidget(
            model=CalendarPeriod,
            depends_on="org_unit",
            placeholder="Select calendar period...",
            search_placeholder="Search calendar periods...",
        ),
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        if request is None or not request.user.is_authenticated:
            return

        org_unit, calendar_period = (
            WorkspaceContextService.get_session_selection(request)
        )

        accessible_org_units = WorkspaceContextService.get_user_org_units(
            request.user
        )

        self.fields["org_unit"].queryset = OrgUnit.objects.filter(
            pk__in=[unit.pk for unit in accessible_org_units]
        ).order_by("level")

        if org_unit and WorkspaceContextService.can_access_org_unit(
            request.user, org_unit
        ):
            self.fields["calendar_period"].queryset = (
                WorkspaceContextService.get_calendar_periods(org_unit.pk)
            )
        else:
            org_unit = None
            calendar_period = None

        self.initial["org_unit"] = org_unit
        self.initial["calendar_period"] = calendar_period