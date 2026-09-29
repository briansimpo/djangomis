from django.db import models
from django.core.exceptions import ValidationError
from djangospice_framework.db.models import BaseModel


class Workflow(BaseModel):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    def __str__(self):
        return self.name

 
class WorkflowOutcome(BaseModel):
    workflow = models.ForeignKey(Workflow, related_name="outcomes", on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_success = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["workflow", "code"], name="uniq_workflow_outcome")]

    def __str__(self):
        return self.name
  
      
   
class WorkflowState(BaseModel):
    workflow = models.ForeignKey(Workflow, related_name="states", on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()
    is_initial = models.BooleanField(default=False)
    is_terminal = models.BooleanField(default=False)
    can_return = models.BooleanField(default=True)
    can_reject = models.BooleanField(default=True)
    outcome = models.ForeignKey(WorkflowOutcome, blank=True, null=True, on_delete=models.SET_NULL)
    on_enter_enabled = models.BooleanField(default=False)
    on_exit_enabled = models.BooleanField(default=False)
    on_transition_enabled = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["workflow", "code"], name="uniq_workflow_state")]

    def __str__(self):
        return f"{self.workflow.code} -> {self.name}"
  
  
class WorkflowAction(BaseModel):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="action_definitions")
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=["workflow", "code"], name="uniq_workflow_action")]

    def __str__(self):
        return f"{self.workflow.code}: {self.name}"
 
   
class WorkflowTransition(BaseModel):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="transitions")
    from_state = models.ForeignKey(WorkflowState, related_name="outgoing", on_delete=models.CASCADE)
    to_state = models.ForeignKey(WorkflowState, related_name="incoming", on_delete=models.CASCADE)
    action = models.ForeignKey(WorkflowAction, on_delete=models.PROTECT)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=["from_state", "action"], name="uniq_workflow_transition")]

    def __str__(self):
        return f"{self.from_state.name} --[{self.action.name}]--> {self.to_state.name}"

    def clean(self):
        super().clean()
        if self.from_state.workflow_id != self.workflow_id:
            raise ValidationError({"from_state": "Source state must belong to the selected workflow."})
        if self.to_state.workflow_id != self.workflow_id:
            raise ValidationError({"to_state": "Target state must belong to the selected workflow."})
        if self.action.workflow_id != self.workflow_id:
            raise ValidationError({"action": "Action definition must belong to the selected workflow."})