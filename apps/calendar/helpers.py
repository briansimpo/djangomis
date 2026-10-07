from django.http import HttpRequest

from apps.calendar.models import CalendarPeriod


CALENDAR_PERIOD_ID_KEY = "calendar_period_id"


# ---------------------------------------------------------------------------
# Calendar Period
# ---------------------------------------------------------------------------

def get_calendar_period(calendar_period_id):
    """
    Return a calendar period by ID.
    """
    if not calendar_period_id:
        return None

    return CalendarPeriod.objects.filter(id=calendar_period_id).first()


def get_open_calendar_period(org_unit_id):
    """
    Return the open calendar period for an org unit.
    """
    return CalendarPeriod.objects.filter(
        org_unit_id=org_unit_id,
        is_open=True,
    ).first()


def get_calendar_periods(org_unit_id):
    # Prevent massive data leak fallback
    if org_unit_id:
        return CalendarPeriod.objects.filter(org_unit_id=org_unit_id).order_by("-start_day")
    else:
        return CalendarPeriod.objects.filter(is_open=True)


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

def get_requested_calendar_period_id(request: HttpRequest):
    """
    Return a valid ID supplied by the request.
    """
    return request.POST.get(CALENDAR_PERIOD_ID_KEY)


def get_requested_calendar_period(request: HttpRequest):
    """
    Return the org unit supplied by the request.
    """
    calendar_period_id = get_requested_calendar_period_id(request)

    return get_calendar_period(calendar_period_id)


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def get_session_calendar_period_id(request: HttpRequest):
    """
    Return the calendar period ID stored in the session.
    """
    return request.session.get(CALENDAR_PERIOD_ID_KEY)


def set_session_calendar_period_id(request: HttpRequest, calendar_period_id: str):
    """
    Store the current calendar period selection in the session.
    """
    request.session[CALENDAR_PERIOD_ID_KEY] = str(calendar_period_id)


def clear_session_calendar_period_id(request: HttpRequest):
    """
    Remove the current calendar period selection from the session.
    """
    request.session.pop(CALENDAR_PERIOD_ID_KEY, None)


def get_session_calendar_period(request: HttpRequest):
    """
    Return the calendar period stored in the session.
    """
    return get_calendar_period(
        get_session_calendar_period_id(request)
    )