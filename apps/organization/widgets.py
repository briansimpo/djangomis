from djangospice.widget import widget
from djangospice.table_widget.widget import TableWidget
from .models import OrgUnit
from .tables import OrgUnitTable
from .filters import OrgUnitFilter


@widget
class OrgUnitTableWidget(TableWidget):
    model = OrgUnit
    table_class = OrgUnitTable
    filterset_class = OrgUnitFilter
    alphabet_field = "name"
    selectable = True
    lazy = True
  