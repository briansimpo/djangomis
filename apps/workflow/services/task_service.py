from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from apps.workflow.enums import DurationUnit
from apps.workflow.models import WorkflowTask
from apps.workflow.enums import TaskStatus
from apps.workflow.models.definitions import WorkflowState
from apps.workflow.models.instances import WorkflowInstance


class TaskService:


    def close_active_tasks(self, instance: WorkflowInstance, actor):

        active_task = instance.tasks.filter(status=TaskStatus.PENDING, assigned_to=actor).first()
    
        instance.tasks.filter(
            status=TaskStatus.PENDING
        ).update(
            status=TaskStatus.COMPLETED,
            completed_at=timezone.now(),
            resolved_at=timezone.now()
        )

        return active_task

    def create_tasks(self, instance: WorkflowInstance, assignees):
        due_at = self.calculate_due_date(instance.current_state)

        tasks = []

        for user in assignees:
            tasks.append(
                WorkflowTask(
                    instance=instance,
                    state=instance.current_state,
                    assigned_to=user,
                    status=TaskStatus.PENDING,
                    due_at=due_at
                )
            )

        WorkflowTask.objects.bulk_create(tasks)

        return tasks
    
    
    def calculate_due_date(self, state:WorkflowState, start_at=None):

        start_at = start_at or timezone.now()

        if not hasattr(state, "sla") or not state.sla:
            return None

        sla = state.sla

        mapping = {
            DurationUnit.MINUTES: timedelta(minutes=sla.duration_value),
            DurationUnit.HOURS: timedelta(hours=sla.duration_value),
            DurationUnit.DAYS: timedelta(days=sla.duration_value),
        }

        delta = mapping.get(sla.duration_unit)

        return start_at + delta if delta else None