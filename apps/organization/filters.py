from djangospice.filters import BaseFilter, LookupChoiceFilter
from .models import OrgUnit


class OrgUnitFilter(BaseFilter):
    parent = LookupChoiceFilter(
        queryset=OrgUnit.objects.all(), 
        field_name="parent", 
        label="Parent", 
    )
    
    class Meta:
        model = OrgUnit
        fields = ["parent"]  
