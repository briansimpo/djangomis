from django.utils.functional import SimpleLazyObject
from apps.calendar.helpers import get_session_calendar_period


def calenda_period_scope(request):
    """
    Makes the active OrgUnit and Period available globally to all templates.
    """
    return {
        "calendar_period": SimpleLazyObject(lambda:get_session_calendar_period(request)),
    }