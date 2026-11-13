from __future__ import annotations

from djangospice.widget import Widget, widget
from djangospice.utils import get_template_name
from djangospice.table.widget import TableWidget
from djangospice.widget.actions import Action, Actions
from apps.organization.helpers import build_org_tree
from .models import OrgUnit
from .tables import OrgUnitTable
from .filters import OrgUnitFilter
from .apps import namespace




@widget
class OrgUnitTableWidget(TableWidget):  
    model = OrgUnit
    title = "Organization Units"
    description = "Manage Organization units which form the Organization structure of your institution"
    table_class = OrgUnitTable
    filterset_class = OrgUnitFilter
    login_required = True
    staff_required = True
    search_fields = ("code", "name")
 

    class BulkEdit(Action):

        def execute(self, context):
            return super().execute(context)


    class BulkDelete(Action):
        def execute(self, context):
            return super().execute(context)


    class RowEdit(Action):

        def execute(self, context):
            return super().execute(context)


    class RowDelete(Action):

        def execute(self, context):
            return super().execute(context)
    

    bulk_actions = Actions(
       BulkEdit(),
       BulkDelete()
    )

    row_actions = Actions(
        RowEdit(),
        RowDelete()
    )
     
   


@widget
class OrgUnitStructureWidget(Widget):
    template_name = get_template_name("widgets/org_structure.html", namespace)
    login_required = True
    staff_required = True

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        context["org_units"] = build_org_tree()
        return context