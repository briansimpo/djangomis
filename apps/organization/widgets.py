
from djangospice.widget import widget
from djangospice.table import Table, Field
from apps.organization.models.orgunits import OrgUnit


@widget
class OrgUnitTable(Table):
    model = OrgUnit
    lazy = True
    selectable = True
    fields = ("code", "name", Field(name="parent", label="Belongs To"))
