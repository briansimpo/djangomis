from django.utils import timezone
from apps.workflow.enums import WorkflowStatus
from apps.workflow.models.definitions import WorkflowTransition
from apps.workflow.models.instances import WorkflowInstance


class StateService:

    def apply_transition(self, instance: WorkflowInstance, transition:WorkflowTransition) -> WorkflowInstance:
        state = transition.to_state
        instance.current_state = state

        if state.is_terminal:
            instance.outcome = state.outcome
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = timezone.now()

        instance.save()
        return instance