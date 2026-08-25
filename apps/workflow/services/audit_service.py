from typing import Any
from apps.workflow.models import WorkflowAction, WorkflowTransition, WorkflowInstance, WorkflowTask


class AuditService:

    def log(self, instance:WorkflowInstance, task:WorkflowTask, transition:WorkflowTransition, actor:Any, comment="", extra_data=None):

        return WorkflowAction.objects.create(
            instance=instance,
            task=task,
            action=transition.action,
            from_state=transition.from_state,
            to_state=transition.to_state,
            actor=actor,
            comment=comment,
            extra_data=extra_data or {}
        )