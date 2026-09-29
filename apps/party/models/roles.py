from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice_framework.db.models import BaseModel, OptionModel
from .parties import Party


class PartyRoleType(OptionModel):
    """
    Lookup registry defining the active capacities a Party can hold inside the system 
    (e.g., 'STUDENT', 'EMPLOYEE', 'ALUMNUS', 'VENDOR', 'SPONSOR').
    Inherits primary code and display name fields from OptionModel.
    """
    class Meta:
        verbose_name = _("Party Role Type")
        verbose_name_plural = _("Party Role Types")

    
class PartyRole(BaseModel):
    """
    The contextual mapping table that activates specific operational capabilities 
    for a Party within a designated timeline.
    """
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name="party_roles",
        verbose_name=_("Party Identity Link"),
        help_text=_("The core party being granted this functional role context.")
    )
    role_type = models.ForeignKey(
        PartyRoleType,
        on_delete=models.PROTECT,
        related_name="party_role_assignments",
        verbose_name=_("Role Type Lookup")
    )
    start_date = models.DateField(
        _("Start Date"),
        blank=True, 
        null=True,
        help_text=_("The calendar date when this role context officially takes effect.")
    )
    end_date = models.DateField(
        _("End Date"),
        blank=True, 
        null=True,
        help_text=_("The scheduled termination, graduation, or expiration date of this assignment.")
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Uncheck to freeze workflows related to this role without wiping history records.")
    )
    
    class Meta:
        verbose_name = _("Party Role")
        verbose_name_plural = _("Party Roles")
        ordering = ["-is_active", "role_type", "-start_date", "-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["party", "role_type"], 
                name="uniq_party_role_assignment"
            )
        ]

    def __str__(self):
        return f"{self.party} ──({self.role_type})"