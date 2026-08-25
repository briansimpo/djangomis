from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice.db.models import BaseModel, OptionModel
from .parties import Party


class PartyTag(OptionModel):
    """
    Lookup taxonomy registry for dynamic labeling (e.g., 'VIP', 'PROSPECT', 'ALUMNI_DONOR', 'BAD_DEBTOR').
    Inherits primary code and display name fields from OptionModel.
    """
    class Meta:
        verbose_name = _("Party Tag")
        verbose_name_plural = _("Party Tags")
  
  
class PartyTagAssignment(BaseModel):
    """
    The intersection table linking a Party to an administrative tag.
    Enforces distinct tag assignments without cluttering core profile schemas.
    """
    party = models.ForeignKey(
        Party, 
        on_delete=models.CASCADE, 
        related_name='party_tags',
        verbose_name=_("Party")
    )
    tag = models.ForeignKey(
        PartyTag, 
        on_delete=models.PROTECT,
        related_name='tag_assignments',
        verbose_name=_("Tag")
    )
    
    class Meta:
        verbose_name = _("Party Tag Assignment")
        verbose_name_plural = _("Party Tag Assignments")
        # Most recently added tags bubble up to the top of records automatically
        ordering = ["-created"]
        constraints = [
            # Safeguards database integrity against assigning the exact same tag 
            # to an identical party multiple times.
            models.UniqueConstraint(
                fields=["party", "tag"], 
                name="uniq_party_tag_assignment"
            )
        ]

    def __str__(self):
        return f"{self.party} {self.tag}"