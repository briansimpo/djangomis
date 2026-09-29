from django.db import models
from django.core.exceptions import ValidationError
from djangospice_framework.db.models import BaseModel
from apps.organization.models import OrgUnit
from apps.workforce.models import Worker, Position
from apps.workflow.enums import ActorSource
from .definitions import WorkflowState


class Actor(BaseModel):
    state = models.ForeignKey(WorkflowState, related_name="actors", on_delete=models.CASCADE)
    source = models.CharField(max_length=100, choices=ActorSource.choices)
    
    worker = models.ForeignKey(Worker, blank=True, null=True, on_delete=models.SET_NULL)
    position = models.ForeignKey(Position, blank=True, null=True, on_delete=models.SET_NULL)
    org_unit = models.ForeignKey(OrgUnit, blank=True, null=True, on_delete=models.SET_NULL)
    
    level = models.PositiveIntegerField(default=1, help_text="Approval depth for relative routing")

    order = models.PositiveIntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    can_delegate = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        actor = self.get_actor() or "Unassigned"
        return f"{self.state} - {self.source}: {actor}"

    def get_actor(self):
        # Updated to return the relevant structural entity
        if self.source == ActorSource.WORKER:
            return self.worker
        if self.source == ActorSource.POSITION:
            return self.position
        if self.source == ActorSource.ORG_UNIT:
            return self.org_unit
        return None

    def clean(self):
        # Ensure data consistency based on the selected source
        if self.source == ActorSource.WORKER and not self.worker:
            raise ValidationError("Worker must be selected when source is WORKER.")
        if self.source == ActorSource.POSITION and not self.position:
            raise ValidationError("Position must be selected when source is POSITION.")