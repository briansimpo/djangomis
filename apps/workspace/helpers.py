from apps.organization.models.orgunits import OrgUnit
from apps.workforce.helpers import get_user_org_unit


def get_user_org_units(user):
    if user.is_superuser:
        return list(OrgUnit.objects.all().order_by("level"))
    else:
        return list(get_user_org_unit(user))


def user_belongs_to_org_unit(user, org_unit_id):
    org_unit = get_user_org_unit(user)

    return (
        org_unit is not None
        and org_unit.pk == org_unit_id
    )
