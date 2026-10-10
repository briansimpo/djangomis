from djangospice.lookup.decorators import register_lookup

from .models import OrgUnit, OrgUnitType


register_lookup(OrgUnit)
register_lookup(OrgUnitType)
