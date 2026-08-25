from django.db import models
from django.utils.translation import gettext_lazy as _


class DelegationStatus(models.TextChoices):
    """
    State machine for temporary authority projection.
    Ensures a strict audit trail for when system permissions are transferred and why they ended.
    """
    PENDING = "PENDING", _("Pending Acceptance")      
    ACTIVE = "ACTIVE", _("Active")         
    EXPIRED = "EXPIRED", _("Expired")       
    REVOKED = "REVOKED", _("Revoked")     
    REJECTED = "REJECTED", _("Rejected")  


class PositionStatus(models.TextChoices):
    """
    State machine for structural corporate seats. 
    Controls budgeting and hiring availability independently of human occupants.
    """
    DRAFT = "DRAFT", _("Draft")              
    ACTIVE = "ACTIVE", _("Active")           
    FROZEN = "FROZEN", _("Frozen")                      
    ABOLISHED = "ABOLISHED", _("Abolished")             



class ContractStatus(models.TextChoices):
    """
    The legal contract state machine between the Worker and the Sponsoring Party.
    """
    PENDING = "PENDING", _("Pending")  
    ACTIVE = "ACTIVE", _("Active")                 
    ON_LEAVE = "ON_LEAVE", _("On Leave")         
    SUSPENDED = "SUSPENDED", _("Suspended")                   
    TERMINATED = "TERMINATED", _("Terminated")                
    EXPIRED = "EXPIRED", _("Expired")             
    ARCHIVED = "ARCHIVED", _("Archived")             


class DeploymentStatus(models.TextChoices):
    """
    The operational state machine. Governs a Worker's active involvement 
    in a specific WorkContext (like a project, squad, or task force).
    """
    PLANNED = "PLANNED", _("Planned")             
    ACTIVE = "ACTIVE", _("Active")                
    ON_HOLD = "ON_HOLD", _("On Hold")               
    COMPLETED = "COMPLETED", _("Completed")                  
    REVOKED = "REVOKED", _("Revoked")             
    

class PlacementStatus(models.TextChoices):
    """
    Lifecycle states for a worker's occupancy within a structural Position.
    """
    PENDING = "PENDING", _("Pending") 
    ACTIVE = "ACTIVE", _("Active")
    SUSPENDED = "SUSPENDED", _("Suspended")
    CONCLUDED = "CONCLUDED", _("Concluded")
    TERMINATED = "TERMINATED", _("Terminated")
    CANCELLED = "CANCELLED", _("Cancelled")