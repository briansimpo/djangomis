from django.http import HttpRequest

from apps.organization.models import OrgUnit


ORG_UNIT_ID_KEY = "org_unit_id"


# ---------------------------------------------------------------------------
# Org Unit
# ---------------------------------------------------------------------------

def get_org_unit(org_unit_id):
    """
    Return an org unit by ID.
    """
    if not org_unit_id:
        return None

    return OrgUnit.objects.filter(id=org_unit_id).first()


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

def get_requested_org_unit_id(request: HttpRequest):
    """
    Return a valid org unit ID supplied by the request.
    """
    return request.POST.get(ORG_UNIT_ID_KEY)

def get_requested_org_unit(request: HttpRequest):
    """
    Return the org unit supplied by the request.
    """
    org_unit_id = get_requested_org_unit_id(request)

    return get_org_unit(org_unit_id)


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def get_session_org_unit_id(request: HttpRequest):
    """
    Return the org unit ID stored in the session.
    """
    return request.session.get(ORG_UNIT_ID_KEY)


def set_session_org_unit_id(request: HttpRequest, org_unit_id):
    """
    Store the current org unit selection in the session.
    """
    request.session[ORG_UNIT_ID_KEY] = str(org_unit_id)


def clear_session_org_unit_id(request: HttpRequest):
    """
    Remove the current org unit selection from the session.
    """
    request.session.pop(ORG_UNIT_ID_KEY, None)


def get_session_org_unit(request: HttpRequest):
    """
    Return the org unit stored in the session.
    """
    return get_org_unit(
        get_session_org_unit_id(request)
    )