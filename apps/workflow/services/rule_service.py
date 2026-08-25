from apps.workflow.enums import RuleOperator
from apps.workflow.models.approvables import ApprovableModel
from apps.workflow.models import WorkflowRule, WorkflowRuleGroup
from apps.workflow.models.definitions import WorkflowTransition


class RuleService:
    
    def evaluate_rule(self, rule: WorkflowRule, target_object: ApprovableModel, metadata: dict) -> bool:
        """Evaluates a single rule against object attributes or JSON metadata."""
        value = metadata.get(rule.field_name, getattr(target_object, rule.field_name, None))
        target = rule.value
        op = rule.operator

        try:
            if op == RuleOperator.EQUAL: 
                return value == target
            if op == RuleOperator.NOT_EQUAL: 
                return value != target
            if op == RuleOperator.GREATER_THAN: 
                return value > target
            if op == RuleOperator.GREATER_OR_EQUAL: 
                return value >= target
            if op == RuleOperator.LESS_THAN: 
                return value < target
            if op == RuleOperator.LESS_OR_EQUAL: 
                return value <= target
            if op == RuleOperator.IN: 
                return value in target
            if op == RuleOperator.CONTAINS: 
                return target in value if value else False
        except (TypeError, ValueError):
            return False
            
        return False

    def evaluate_transition(self, transition: WorkflowTransition, target_object: ApprovableModel, metadata: dict) -> bool:
        """Determines if a transition is permitted based on associated rules."""
        rules = transition.rules.all()
        groups = transition.rule_groups.all()

        # Handle rules floating outside of a group (Implicit AND)
        solo_rules = [r for r in rules if r.group_id is None]
        solo_ok = all(self.evaluate_rule(r, target_object, metadata) for r in solo_rules)

        # Handle explicit logical groups
        if groups.exists():
            group_ok = any(self._evaluate_group(g, target_object, metadata) for g in groups)
        else:
            group_ok = True

        return solo_ok and group_ok

    def _evaluate_group(self, group: WorkflowRuleGroup, target_object: ApprovableModel, metadata: dict) -> bool:
        rules = group.rules.all()
        if not rules.exists():
            return True

        if group.operator == "AND":
            return all(self.evaluate_rule(r, target_object, metadata) for r in rules)
            
        # Default to OR
        return any(self.evaluate_rule(r, target_object, metadata) for r in rules)