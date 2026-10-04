from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from djangospice.db.models import BaseModel
from apps.workflow.enums import DurationUnit, EscalationStrategy
from .definitions import WorkflowState

User = get_user_model()


class SLA(BaseModel):
    state = models.OneToOneField(WorkflowState, on_delete=models.CASCADE, related_name="sla")
    duration_value = models.PositiveIntegerField()
    duration_unit = models.CharField(max_length=20, choices=DurationUnit.choices)
    escalation_strategy = models.CharField(max_length=30, choices=EscalationStrategy.choices, default=EscalationStrategy.NOTIFY)
    escalation_state = models.ForeignKey(WorkflowState, related_name="escalated_slas", on_delete=models.SET_NULL, blank=True, null=True)
    escalation_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    escalation_group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"SLA for {self.state} ({self.duration_value} {self.duration_unit})"