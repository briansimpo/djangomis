from django import forms

from djangospice.lookup.widget import LookupWidget
from djangospice.forms.mixins import FormRequestMixin
from apps.organization.models import OrgUnit
from apps.calendar.models import CalendarPeriod
from .services import WorkspaceContextService


class WorkspaceContextForm(FormRequestMixin, forms.Form):
    org_unit = forms.ModelChoiceField(
        label="Organisation Unit",
        queryset=OrgUnit.objects.none(),
        required=True,
        widget=LookupWidget(
            model=OrgUnit,
            placeholder="Select organisation unit...",
            search_placeholder="Search organisation units...",
        ),
    )

    calendar_period = forms.ModelChoiceField(
        label="Calendar Period",
        queryset=CalendarPeriod.objects.none(),
        required=True,
        widget=LookupWidget(
            model=CalendarPeriod,
            depends_on="org_unit",
            placeholder="Select calendar period...",
            search_placeholder="Search calendar periods...",
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.request and not self.request.user.is_authenticated:
            return

        org_unit, calendar_period = WorkspaceContextService.get_session_selection(self.request)
        

        user_org_units = WorkspaceContextService.get_user_org_units(self.request.user)

        org_units_uuids =  [org_unit.pk for org_unit in user_org_units]

        org_units_queryset = OrgUnit.objects.filter(pk__in=org_units_uuids).order_by("level")

        self.fields["org_unit"].queryset = org_units_queryset

        can_access_org_unit = WorkspaceContextService.can_access_org_unit(self.request.user, org_unit)

        if org_unit and can_access_org_unit:
            self.fields["calendar_period"].queryset = WorkspaceContextService.get_calendar_periods(org_unit.pk)
        else:
            org_unit = None
            calendar_period = None

        self.initial["org_unit"] = org_unit
        self.initial["calendar_period"] = calendar_period
