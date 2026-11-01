import django_filters
from djangospice.filters.base import BaseFilter
from djangospice.lookup import LookupWidget
from .models import OrgUnit


class OrgUnitFilter(BaseFilter):
    parent = django_filters.ModelChoiceFilter(
        queryset=OrgUnit.objects.all(), 
        field_name="parent", 
        label="Parent", 
        widget=LookupWidget(model=OrgUnit, placeholder="Search parent"),
    )
    
    class Meta:
        model = OrgUnit
        fields = ["code", "name", "parent"]  
