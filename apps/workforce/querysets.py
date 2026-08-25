from django.db import models
from django.db.models import Q
from apps.organization.models import OrgUnitClosure

class WorkforceScopeQuerySet(models.QuerySet):
    
    def authorized(self, request):
        if not hasattr(request, 'workforce') or not request.workforce.is_active_worker:
            return self.none()

        wf = request.workforce
        
        # Determine the scope of OrgUnits the user has access to
        if wf.org_unit:
            # Fetch the IDs of the current OrgUnit and all its descendants
            # using the Closure Table
            org_unit_ids = OrgUnitClosure.objects.filter(
                ancestor=wf.org_unit
            ).values_list("descendant_id", flat=True)
            
            # Include the current unit itself
            scope_ids = list(org_unit_ids) + [wf.org_unit.id]
        else:
            # Fallback if no org_unit is assigned (e.g., restricted access)
            scope_ids = []

        # Scope the queryset
        return self.filter(
            Q(worker=wf.worker) | 
            Q(worker__supervisor=wf.worker) | 
            Q(org_unit_id__in=scope_ids)
        ).distinct()