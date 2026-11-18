from djangospice.table.base import BaseTable

from apps.organization.models.orgunits import OrgUnit

class OrgUnitTable(BaseTable):

    class Meta:
        model = OrgUnit
        fields = ["code", "name", "type", "parent", "level"]