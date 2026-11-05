import django_tables2 as tables
from djangospice.table.base import BaseTable
from .models import OrgUnit


class OrgUnitTable(BaseTable):
    
    code = tables.Column(
        verbose_name="Code",
        accessor="code",
    )

    name = tables.Column(
        verbose_name="Name",
        accessor="name",
    )

    parent = tables.Column(
        verbose_name="Parent",
        accessor="parent",
    )
    
   
    class Meta:
        model = OrgUnit
        fields = [
            "selection", "code", "name", "parent",
        ]
