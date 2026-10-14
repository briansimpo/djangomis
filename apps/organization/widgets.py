from djangospice.widget import widget
from djangospice.table import Table
from .models import OrgUnit
from .filters import OrgUnitFilter


@widget
class OrgUnitTable(Table):
    model = OrgUnit
    lazy = True
    alphabet_field = "name"
    selectable = True
    fields = ("code", "name", "parent")
    filterset_class = OrgUnitFilter
