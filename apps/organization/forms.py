from djangospice.forms import DynamicModelForm

from apps.organization.models.orgunits import OrgUnit

class OrgUnitForm(DynamicModelForm):

    class Meta:
        model = OrgUnit
        fields = ["code", "name", "type", "parent", "level"]
