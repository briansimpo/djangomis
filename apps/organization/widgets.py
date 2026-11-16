from __future__ import annotations

from djangospice.widget import Widget, widget
from djangospice.http.shortcuts import htmx_navigate
from djangospice.utils import get_template_name, safe_reverse
from djangospice.table.widget import TableWidget
from djangospice.table.decorators import row_action, bulk_action

from .helpers import build_org_tree
from .skeletons import OrgStructureSkeleton
from .models import OrgUnit
from .filters import OrgUnitFilter
from .apps import namespace


@widget
class OrgUnitTable(TableWidget):  
    title = "Organization Units"
    description = "Manage Organization units which form the Organization structure of your institution"
    model = OrgUnit
    fields = ("code", "name", "type", "parent", "level")
    search_fields = ("code", "name")
    filterset_class = OrgUnitFilter
    login_required = True
    staff_required = True

    def get_row_url(self):
        return safe_reverse(
            view_name="edit_org_unit",
            app_name=namespace,
            placeholder=True,
        )
            
    @bulk_action(
        label="Set Active",
        icon="fa-solid fa-check-circle",
        order=1,
    )
    def activate(self):
        selected_ids = self.get_selected_rows()
        return self.response(selected_ids)

    @bulk_action(
        label="Set Inactive",
        icon="fa-solid fa-ban",
        order=2,
    )
    def deactivate(self):
        selected_ids = self.get_selected_rows()
        return self.response(selected_ids)

    @bulk_action(
        label="Export Selected",
        icon="fa-solid fa-file-export",
        order=3,
    )
    def export(self):
        selected_ids = self.get_selected_rows()
        return self.response(selected_ids)

    @bulk_action(
        label="Delete Selected",
        icon="fa-solid fa-trash-can",
        order=4,
        style="danger",
        is_danger=True,
        confirm="Are you sure you want to delete the selected records?",
    )
    def delete_all(self):
        selected_ids = self.get_selected_rows()
        return self.response(selected_ids)

    @row_action(
        label="View Details",
        icon="fa-solid fa-eye",
        order=1,
        is_link=True,
    )
    def view(self):
        selected_id = self.get_selected_row()
        url = safe_reverse(
            view_name="edit_org_unit",
            app_name=namespace,
            args=[selected_id]
        )
        return htmx_navigate(url)

    @row_action(
        label="Edit Record",
        icon="fa-solid fa-pen",
        order=2,
        is_link=True,
    )
    def edit(self):
        selected_id = self.get_selected_row()
        return self.response(selected_id)

    @row_action(
        label="Delete Record",
        icon="fa-solid fa-trash",
        order=3,
        style="danger",
        is_danger=True,
        confirm="Delete this organizational unit?",
    )
    def delete(self):
        selected_id = self.get_selected_row()
        return self.response(selected_id)
    

@widget
class OrgUnitStructure(Widget):
    template_name = get_template_name("widgets/org_structure.html", namespace)
    login_required = True
    staff_required = True

    def get_skeleton(self):
        return OrgStructureSkeleton()

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        context["org_units"] = build_org_tree()
        return context