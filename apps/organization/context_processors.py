from django.utils.functional import SimpleLazyObject
from apps.organization.helpers import get_session_org_unit
from .models import Company


def org_metadata(request):
    org = Company.objects.first()
    return {"org": org}


def org_unitscope(request):

    return {
        "org_unit": SimpleLazyObject(lambda: get_session_org_unit(request))
    }