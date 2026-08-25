from abc import ABC, abstractmethod


class WorkflowHandler(ABC):
    """Inherit from this class to implement automated execution hooks."""
    
    @abstractmethod
    def execute(self, context: dict) -> None:
        raise NotImplementedError("Subclasses must implement the execute method.")