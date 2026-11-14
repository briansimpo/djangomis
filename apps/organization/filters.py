from djangospice.filters import BaseFilter, LookupChoiceFilter
from .models import OrgUnit, OrgUnitType


class OrgUnitFilter(BaseFilter):
    type = LookupChoiceFilter(
        model=OrgUnitType, 
        field_name="type", 
        label="Type", 
    )
    parent = LookupChoiceFilter(
        model=OrgUnit, 
        field_name="parent", 
        label="Parent", 
    )
    
    class Meta:
        model = OrgUnit
        fields = ["type", "parent"]  
