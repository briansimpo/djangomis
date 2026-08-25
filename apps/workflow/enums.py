from django.db import models


class WorkflowStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    RETURNED = "RETURNED", "Returned"


class TaskStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ASSIGNED = "ASSIGNED", "Assigned"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    SKIPPED = "SKIPPED", "Skipped"
    ESCALATED = "ESCALATED", "Escalated"


class ActorSource(models.TextChoices):
    WORKER = "WORKER", "Staff"
    POSITION = "POSITION", "Position"
    SUPERVISOR = "SUPERVISOR", "Supervisor"
    ORG_UNIT = "ORG_UNIT", "Org Unit Head"
    APPROVAL_CHAIN = "APPROVAL_CHAIN", "Initiator Manager"


class DurationUnit(models.TextChoices):
    MINUTE = "MINUTE", "Minute"
    HOUR = "HOUR", "Hour"
    DAY = "DAY", "Day"
    WEEK = "WEEK", "Week"
    MONTH = "MONTH", "Month"


class EscalationStrategy(models.TextChoices):
    NONE = "NONE", "No Escalation"
    NOTIFY = "NOTIFY", "Notify"
    REASSIGN = "REASSIGN", "Reassign"
    ESCALATE = "ESCALATE", "Escalate"
    AUTO_APPROVE = "AUTO_APPROVE", "Auto Approve"
    AUTO_REJECT = "AUTO_REJECT", "Auto Reject"


class RuleOperator(models.TextChoices):
    EQUAL = "EQ", "="
    NOT_EQUAL = "NE", "!="
    GREATER_THAN = "GT", ">"
    GREATER_OR_EQUAL = "GTE", ">="
    LESS_THAN = "LT", "<"
    LESS_OR_EQUAL = "LTE", "<="
    IN = "IN", "In"
    NOT_IN = "NOT_IN", "Not In"
    CONTAINS = "CONTAINS", "Contains"