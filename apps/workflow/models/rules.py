from django.db import models
from django.core.exceptions import ValidationError
from djangospice.db.models import BaseModel
from apps.workflow.enums import RuleOperator
from .definitions import WorkflowTransition


class WorkflowRuleGroup(BaseModel):
    transition = models.ForeignKey(WorkflowTransition, related_name="rule_groups", on_delete=models.CASCADE)
    operator = models.CharField(max_length=3, choices=[("AND", "AND"), ("OR", "OR")], default="AND")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Group {self.order} ({self.operator}) for Transition: {self.transition_id}"
   

class WorkflowRule(BaseModel):
    transition = models.ForeignKey(WorkflowTransition, related_name="rules", on_delete=models.CASCADE)
    group = models.ForeignKey(WorkflowRuleGroup, related_name="rules", on_delete=models.CASCADE, blank=True, null=True)
    field_name = models.CharField(max_length=100)
    operator = models.CharField(max_length=20, choices=RuleOperator.choices)
    value = models.JSONField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.field_name} {self.operator} {self.value}"

    def clean(self):
        super().clean()
        if self.group and self.group.transition_id != self.transition_id:
            raise ValidationError({"group": "Rule group must belong to the exact same transition as the rule."})