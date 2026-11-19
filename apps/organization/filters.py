from djangospice.filters import DynamicFilter
from .models import OrgUnit


class OrgUnitFilter(DynamicFilter):
    
    class Meta:
        model = OrgUnit
        fields = ["type", "parent"]  
