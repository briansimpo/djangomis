from django.utils.functional import SimpleLazyObject
from apps.organization.helpers import get_session_org_unit
from .models import Company


def org_meta_data(request):
    org = Company.objects.first()
    return {"org": org}


def org_unit_scope(request):

    return {
        "org_unit": SimpleLazyObject(lambda: get_session_org_unit(request))
    }