import logging
from django.utils import timezone
from django.db import transaction
from apps.workflow.models import WorkflowTask
from apps.workflow.enums import TaskStatus, EscalationStrategy
from apps.workflow.engines.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)


class EscalationEngine:
    
    def __init__(self):
        self.executor = WorkflowEngine()

    @transaction.atomic
    def process_breaches(self):
        """Scans all system tasks, trapping expired timers and triggering escalations."""
        now = timezone.now()
        breached_tasks = WorkflowTask.objects.filter(
            status=TaskStatus.PENDING,
            due_at__lt=now,
            is_breached=False
        ).select_related("state__sla", "instance")

        for task in breached_tasks:
            self.escalate_task(task, now)

    def escalate_task(self, task: WorkflowTask, execution_time):
        """Applies the specific SLA mitigation strategy configured for the task."""
        task.is_breached = True
        task.breached_at = execution_time
        task.save()

        state = task.state
        if not hasattr(state, "sla") or not state.sla:
            return

        sla = state.sla
        instance = task.instance
        
        logger.warning(f"SLA Breach detected on Task #{task.id}. Executing strategy: {sla.escalation_strategy}")

        # Strategy A: Silent System Alert / Notification Broadcast
        if sla.escalation_strategy == EscalationStrategy.NOTIFY:
            # Placeholder: Hook into your notification dispatcher system here
            # notification_service.send_sla_alert(instance, target=sla.escalation_user)
            pass

        # Strategy B: Route Task ownership to an alternate group or supervisor
        elif sla.escalation_strategy == EscalationStrategy.REASSIGN:
            task.status = TaskStatus.ESCALATED
            task.save()

            WorkflowTask.objects.create(
                instance=instance,
                state=state,
                assigned_to=sla.escalation_user,
                assigned_group=sla.escalation_group,
                status=TaskStatus.PENDING,
                due_at=None  # Escalated tasks escape normal SLAs to prevent loops
            )

       