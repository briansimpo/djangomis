from djangospice.forms import DynamicModelForm, LookupMultipleChoiceField

from apps.organization.models.orgunits import OrgUnit, OrgUnitType

class OrgUnitForm(DynamicModelForm):
    type = LookupMultipleChoiceField(queryset=OrgUnitType.objects.all())

    class Meta:
        model = OrgUnit
        fields = ["code", "name", "type", "parent", "level"]
