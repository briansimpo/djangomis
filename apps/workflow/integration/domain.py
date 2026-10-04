from django.core.exceptions import ValidationError
from apps.workflow.models import Workflow


class ApprovalState:
    
    def __init__(self,code, name, order,is_terminal=False):
        self.code = code
        self.name = name
        self.order = order
        self.is_terminal = is_terminal

        self.validate()

    def validate(self):
        errors = {}
        
        if not self.code or not str(self.code).strip():
            errors["code"] = "State code is required."


        # Required string fields
        if not self.name or not str(self.name).strip():
            errors["name"] = "State name is required."

        # Required numeric fields
        if self.order is None:
            errors["order"] = "State order is required."
        elif not isinstance(self.order, int):
            errors["order"] = "State order must be an integer."
        elif self.order <= 0:
            errors["order"] = "State order must be greater than 0."
            
        if errors:
            raise ValidationError(errors)


class ApprovalWorkflow:
    code = None
    name = None
    description = None

    states = [
        ApprovalState(
            code="Stage 1",
            name="Stage 1",
            order=1
        ),
        ApprovalState(
            code="Stage 2",
            name="Stage 2",
            order=2,
        ),
        ApprovalState(
            code="Stage 3",
            name="Stage 3",
            order=3,
            is_terminal=True,
        ),
    ]

    def __init__(self):
        self.validate()

    def validate(self):
        errors = {}

        # Required workflow fields
        if not self.code or not str(self.code).strip():
            errors["code"] = "Workflow code is required."

        if not self.name or not str(self.name).strip():
            errors["name"] = "Workflow name is required."

        # Validate states
        if not self.states:
            errors["states"] = "Workflow must contain at least one State."

        else:
            orders = []
            terminal_states = []

            for index, step in enumerate(self.states):
                if not isinstance(step, ApprovalState):
                    raise ValidationError(
                        f"Invalid step object at index {index}."
                    )

                orders.append(step.order)

                if step.is_terminal:
                    terminal_states.append(step)

            # Ensure unique orders
            duplicate_orders = {
                order for order in orders if orders.count(order) > 1
            }

            if duplicate_orders:
                errors["states_order"] = (
                    f"Duplicate step orders found: "
                    f"{sorted(list(duplicate_orders))}"
                )

            # Ensure exactly one terminal step
            if len(terminal_states) == 0:
                errors["terminal_step"] = (
                    "Workflow must have one terminal step."
                )

            elif len(terminal_states) > 1:
                errors["terminal_step"] = (
                    "Workflow cannot have multiple terminal states."
                )

        if errors:
            raise ValidationError(errors)

    def get_workflow(self) -> Workflow:
        if not self.code:
            raise ValidationError(
                {"code": "Workflow code cannot be empty."}
            )

        return Workflow.objects.get(code=self.code)