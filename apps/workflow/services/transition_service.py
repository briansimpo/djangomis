from typing import List

from apps.workflow.exceptions import TransitionNotFoundError
from apps.workflow.models.definitions import WorkflowAction, WorkflowTransition
from apps.workflow.models.instances import WorkflowInstance
from apps.workflow.services.rule_service import RuleService


class TransitionService:

    def __init__(self, rule_service: RuleService):
        self.rule_service = rule_service

    def get_valid_transitions(self, instance: WorkflowInstance) -> List[WorkflowTransition]:
        state = instance.current_state
        transitions = state.outgoing.select_related("to_state", "action")

        valid_transitions = []
        for transition in transitions:
            if self.rule_service.evaluate_transition(transition, instance.content_object, instance.metadata):
                valid_transitions.append(transition)

        # Sort so default paths naturally float to the top
        return sorted(valid_transitions, key=lambda x: x.is_default, reverse=True)

    def resolve(self, instance: WorkflowInstance, action: WorkflowAction) -> WorkflowTransition:
        transitions = self.get_valid_transitions(instance)

        transition = next(
            (t for t in transitions if t.action_id == action.id),
            None
        )

        if not transition:
            raise TransitionNotFoundError(f"Action '{action}' is invalid or blocked by rules.")

        return transition