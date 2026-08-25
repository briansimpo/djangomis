
from .domain import ApprovalWorkflow


class WorkflowRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, workflow_class=None):
      
        def wrapper(cls):
            if not issubclass(cls, ApprovalWorkflow):
                raise TypeError("Only subclasses of ApprovalWorkflow can be registered.")
            
            code = cls.code
            self._registry[code] = cls
            return cls

        # If called as @register (no arguments or class passed directly)
        if workflow_class is None:
            return wrapper

        # If called as @register(MyClass) or registry.register(MyClass)
        return wrapper(workflow_class)

    def get_all(self) -> dict[ApprovalWorkflow]:
        return self._registry.values()

# Global instance
registry = WorkflowRegistry()