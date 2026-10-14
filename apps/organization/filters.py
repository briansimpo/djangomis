from django.db.models import Q
import django_filters
from djangospice.filters import BaseFilter
from djangospice.lookup import LookupWidget
from .models import OrgUnit


class OrgUnitFilter(BaseFilter):
    parent = django_filters.ModelChoiceFilter(
        queryset=OrgUnit.objects.all(), 
        field_name="parent", 
        label="Parent", 
        widget=LookupWidget(model=OrgUnit, placeholder="Search parent"),
    )
    
    def evaluate(self, value):
        return ( 
            Q(code__icontains=value) | 
            Q(name__icontains=value) 
        )
    
    class Meta:
        model = OrgUnit
        fields = ["parent"]  
