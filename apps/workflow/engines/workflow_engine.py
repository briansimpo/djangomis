from typing import Any, Dict, Optional, Type
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from apps.workflow.models.approvables import ApprovableModel
from apps.workflow.integration.domain import ApprovalWorkflow
from apps.workflow.enums import TaskStatus, WorkflowStatus
from apps.workflow.exceptions import WorkflowException
from apps.workflow.models.definitions import WorkflowAction
from apps.workflow.models.instances import WorkflowInstance

from apps.workflow.services.approver_service import ApproverService
from apps.workflow.services.rule_service import RuleService
from apps.workflow.services.transition_service import TransitionService
from apps.workflow.services.task_service import TaskService
from apps.workflow.services.audit_service import AuditService
from apps.workflow.services.state_service import StateService


class WorkflowEngine:
    """
    Orchestrates the lifecycle, state transitions, and task management 
    of approval workflows within the system.
    """

    def __init__(self) -> None:
        """Initializes the workflow engine and its internal services."""
        self.rule_service = RuleService()
        self.transition_service = TransitionService(self.rule_service)
        self.task_service = TaskService()
        self.audit_service = AuditService()
        self.state_service = StateService()
        self.approver_service = ApproverService()
        
    @transaction.atomic
    def create(self, approvable_instance: ApprovableModel, workflow_class: Type[ApprovalWorkflow], metadata: Optional[Dict[str, Any]] = None) -> WorkflowInstance:
        """
        Creates or updates a draft WorkflowInstance for a given approvable_instance.

        Args:
            approvable_instance: The business object requiring approval. Must inherit from Approvable.
            workflow_class: The workflow definition class. Must inherit from ApprovalWorkflow.
            metadata: Optional dictionary for storing additional workflow context.

        Returns:
            WorkflowInstance: The newly created or updated workflow instance.

        Raises:
            ValidationError: If the approvable_instance or workflow_class are of incorrect types.
        """
        metadata = metadata or {}

        if not isinstance(approvable_instance, ApprovableModel):
            raise ValidationError("approvable_instance must inherit from Approvable.")

        if not issubclass(workflow_class, ApprovalWorkflow):
            raise ValidationError("workflow_class must inherit from ApprovalWorkflow.")

        workflow = workflow_class().get_workflow()
        content_type = ContentType.objects.get_for_model(approvable_instance)

        instance, _ = WorkflowInstance.objects.update_or_create(
            content_type=content_type,
            object_id=approvable_instance.pk,
            defaults={
                "workflow": workflow,
                "initiated_by": approvable_instance.submitted_by,
                "org_unit": approvable_instance.org_unit,
                "status": WorkflowStatus.DRAFT,
                "current_state": None,
                "submitted_at": None,
                "completed_at": None,
                "outcome": None,
                "metadata": metadata,
            }
        )

        return instance
    
    @transaction.atomic
    def submit(self, instance: WorkflowInstance) -> WorkflowInstance:
        """
        Submits a draft workflow, setting it to its initial state and creating tasks.

        Args:
            instance: The draft WorkflowInstance to submit.

        Returns:
            WorkflowInstance: The submitted workflow instance.

        Raises:
            WorkflowException: If the workflow is not in DRAFT status or lacks an initial state.
        """
        if instance.status != WorkflowStatus.DRAFT:
            raise WorkflowException("Workflow is already submitted.")

        initial_state = instance.workflow.states.filter(is_initial=True).first()
        if not initial_state:
            raise WorkflowException("Workflow has no initial state.")

        instance.current_state = initial_state
        instance.status = WorkflowStatus.SUBMITTED
        instance.submitted_at = timezone.now()

        instance.save(update_fields=["current_state", "status", "submitted_at"])
        self._create_state_tasks(instance)

        return instance
    
    @transaction.atomic
    def resubmit(self, instance: WorkflowInstance) -> WorkflowInstance:
        """
        Resubmits a returned workflow, cancelling pending tasks and resetting its status.

        Args:
            instance: The returned WorkflowInstance to resubmit.

        Returns:
            WorkflowInstance: The resubmitted workflow instance.

        Raises:
            WorkflowException: If the workflow is not in a RETURNED status.
        """
        if instance.status != WorkflowStatus.RETURNED:
            raise WorkflowException("Workflow is not returned.")

        instance.tasks.filter(status=TaskStatus.PENDING).update(
            status=TaskStatus.CANCELLED,
            resolved_at=timezone.now()
        )

        instance.status = WorkflowStatus.SUBMITTED
        instance.save(update_fields=["status"])
        
        self._create_state_tasks(instance)

        return instance
    
    @transaction.atomic
    def move_next(self, instance: WorkflowInstance, action: WorkflowAction, actor: Any, comment: str = "", extra_data: Optional[Dict[str, Any]] = None) -> WorkflowInstance:
        """
        Progresses the workflow to the next state based on the provided action.

        Args:
            instance: The active WorkflowInstance.
            action: The WorkflowAction driving the transition.
            actor: The user or system account performing the action.
            comment: Optional comment accompanying the transition.
            extra_data: Optional dictionary of additional context data.

        Returns:
            WorkflowInstance: The updated workflow instance.

        Raises:
            WorkflowException: If the workflow is already completed and cannot move.
        """
        if not instance.can_move():
            raise WorkflowException("Workflow is already completed.")

        transition = self.transition_service.resolve(instance, action)
        task = self.task_service.close_active_tasks(instance, actor)

        self.audit_service.log(
            instance=instance,
            task=task,
            transition=transition,
            actor=actor,
            comment=comment,
            extra_data=extra_data,
        )

        self.state_service.apply_transition(instance, transition)

        if instance.current_state.is_terminal:
            self._complete_workflow(instance, actor, transition)
            return instance

        self._create_state_tasks(instance)

        return instance
    
    @transaction.atomic
    def return_for_correction(self, instance: WorkflowInstance, actor: Any, comment: str = "") -> WorkflowInstance:
        """
        Returns a workflow to the initiator for correction, closing active tasks.

        Args:
            instance: The WorkflowInstance to return.
            actor: The user performing the return.
            comment: The reason for returning the workflow.

        Returns:
            WorkflowInstance: The updated workflow instance.
        """
        task = self.task_service.close_active_tasks(instance, actor)
        instance.status = WorkflowStatus.RETURNED
        instance.save(update_fields=["status"])

        self.audit_service.log_return(
            instance=instance,
            task=task,
            actor=actor,
            comment=comment,
        )

        return instance
    
    @transaction.atomic
    def restart(self, instance: WorkflowInstance) -> WorkflowInstance:
        """
        Completely restarts a workflow instance, clearing history and pending tasks.

        Args:
            instance: The WorkflowInstance to restart.

        Returns:
            WorkflowInstance: The cleanly restarted workflow instance.
        """
        instance.tasks.all().delete()
        instance.events.all().delete()

        initial_state = instance.workflow.states.filter(is_initial=True).first()

        instance.current_state = initial_state
        instance.status = WorkflowStatus.SUBMITTED
        instance.completed_at = None
        instance.outcome = None
        instance.save()

        self._create_state_tasks(instance)

        return instance
    
    def _create_state_tasks(self, instance: WorkflowInstance) -> None:
        """
        Internal helper to resolve approvers and generate tasks for the current state.
        
        Args:
            instance: The active WorkflowInstance.
        """
        approvers = self.approver_service.get_approvers(instance.current_state)
        self.task_service.create_tasks(instance, approvers)
    
    def _complete_workflow(self, instance: WorkflowInstance, actor: Any, transition: Any) -> None:
        """
        Internal helper to finalize a workflow and trigger its defined outcomes.

        Args:
            instance: The active WorkflowInstance completing its lifecycle.
            actor: The user whose action completed the workflow.
            transition: The final transition that led to completion.
        """
        instance.status = WorkflowStatus.COMPLETED
        instance.completed_at = timezone.now()
        instance.save(update_fields=["status", "completed_at"])

        if instance.outcome:
            context = {
                "instance": instance,
                "actor": actor,
                "transition": transition,
            }
            #dispatch event
            
            
            
