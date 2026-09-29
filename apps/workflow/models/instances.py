from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from djangospice_framework.db.models import BaseModel
from apps.workflow.enums import TaskStatus, WorkflowStatus
from apps.workflow.models.approvables import BaseApprovableModel
from .definitions import Workflow, WorkflowState, WorkflowAction


User = get_user_model()


class WorkflowInstance(BaseApprovableModel):
    workflow = models.ForeignKey(Workflow, on_delete=models.PROTECT, related_name="instances")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")
    current_state = models.ForeignKey(WorkflowState, null=True, on_delete=models.SET_NULL, related_name="current_instances")
    completed_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        indexes = [models.Index(fields=["content_type", "object_id"], name="idx_workflow_instance_gfk")]

    def __str__(self):
        return f"{self.workflow.name} Instance #{self.id} ({self.status})"
    
    def is_active(self):
        return self.status == WorkflowStatus.SUBMITTED
    
    def can_move(self):
        return self.status not in [WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED]
    

class WorkflowTask(BaseModel):
    instance = models.ForeignKey(WorkflowInstance, related_name="tasks", on_delete=models.CASCADE)
    state = models.ForeignKey(WorkflowState, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="workflow_tasks")
    assigned_group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=30, choices=TaskStatus.choices, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    breached_at = models.DateTimeField(blank=True, null=True)
    is_breached = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"Task {self.id} for {self.instance} [{self.status}]"
    
    
class WorkflowActionLog(BaseModel):
    instance = models.ForeignKey(WorkflowInstance, related_name="actions", on_delete=models.CASCADE)
    task = models.ForeignKey(WorkflowTask, blank=True, null=True, on_delete=models.SET_NULL)
    action = models.ForeignKey(WorkflowAction, on_delete=models.PROTECT)
    from_state = models.ForeignKey(WorkflowState, related_name="+", on_delete=models.PROTECT)
    to_state = models.ForeignKey(WorkflowState, related_name="+", on_delete=models.PROTECT)
    actor = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Log {self.id}: {self.actor} executed {self.action} on {self.instance}"