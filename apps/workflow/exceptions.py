class WorkflowException(Exception):
    """Base exception for all workflow engine runtime runtime errors."""
    pass

class RuleValidationError(WorkflowException):
    """Raised when an action is rejected by business rule evaluations."""
    pass

class TransitionNotFoundError(WorkflowException):
    """Raised when an action is unsupported by the current state blueprint."""
    pass