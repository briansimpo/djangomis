from djangospice.forms import DynamicModelForm
from djangospice.forms.inline import Inline

from apps.organization.models.orgunits import OrgUnit, OrgUnitType


class OrgUnitForm(DynamicModelForm):
    class Meta:
        model = OrgUnit
        fields = ["code", "name", "type",  "parent"]


class OrgUnitTypeForm(DynamicModelForm):
    class Meta:
        model = OrgUnitType
        fields = ["code", "name"]
        inlines = [
            Inline(relation="org_unit", form=OrgUnitForm)
        ]
