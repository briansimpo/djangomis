from django import template

from djangospice.templates import get_template_name

from apps.calendar.helpers import get_session_calendar_period_id, get_calendar_periods
from apps.organization.helpers import get_session_org_unit_id
from workspace.helpers import get_user_org_units
from workspace.apps import namespace


register = template.Library()


@register.inclusion_tag(
    get_template_name("components/org_unit_switcher.html", namespace),
    takes_context=True,
)
def org_unit_switcher(context):
    request = context.get("request")

    if not request or not request.user.is_authenticated:
        return {
            "org_units": [],
            "selected_unit_id": None,
        }

    return {
        "org_units": get_user_org_units(request.user),
        "selected_unit_id": get_session_org_unit_id(request),
    }


@register.inclusion_tag(
    get_template_name( "components/calendar_period_switcher.html",  namespace),
    takes_context=True,
)
def calendar_switcher(context):
    request = context.get("request")

    if not request or not request.user.is_authenticated:
        return {
            "periods": [],
            "selected_period_id": None,
        }

    org_unit_id = get_session_org_unit_id(request)

    return {
        "calendar_periods": get_calendar_periods(org_unit_id),
        "selected_period_id": get_session_calendar_period_id(request),
    }