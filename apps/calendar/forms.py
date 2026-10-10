from django import forms

from djangospice.lookup.widget import LookupWidget

from .models import CalendarPeriod, OrgUnit


class AcademicContextForm(forms.Form):
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