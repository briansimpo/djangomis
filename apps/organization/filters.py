from djangospice.filters import BaseFilter, LookupChoiceFilter
from .models import OrgUnit, OrgUnitType


class OrgUnitFilter(BaseFilter):
    type = LookupChoiceFilter(
        queryset=OrgUnitType.objects.all(), 
        field_name="type", 
        label="Type", 
    )
    parent = LookupChoiceFilter(
        queryset=OrgUnit.objects.all(), 
        field_name="parent", 
        label="Parent", 
    )
    
    class Meta:
        model = OrgUnit
        fields = ["type", "parent"]  
