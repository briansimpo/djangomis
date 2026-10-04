from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice.db.models import BaseModel, OptionModel
from .parties import Party


class RelationshipType(OptionModel):
    """
    Lookup matrix specifying structural and legal ties between parties 
    (e.g., 'EMPLOYER_OF', 'PARENT_OF', 'GUARDIAN_OF', 'SUBSIDIARY_OF').
    Inherits primary code and display name fields from OptionModel.
    """
    inverse_name = models.CharField(
        _("Inverse Name"),
        max_length=100,
        help_text=_("The matching title when looking at the link in reverse (e.g., 'Employee' if the name is 'Employer').")
    )
    
    class Meta:
        verbose_name = _("Relationship Type")
        verbose_name_plural = _("Relationship Types")

    def __str__(self):
        # Gracefully fall back to standard string display inherited from OptionModel
        return getattr(self, 'name', super().__str__())
    
    
class PartyRelationship(BaseModel):
    """
    A graph-like connection link joining any two Parties under a specific 
    relationship role with strict effective-dating controls.
    """
    source_party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name="outgoing_relationships",
        verbose_name=_("Source Party"),
        help_text=_("The originating party of the relational connection.")
    )
    target_party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name="incoming_relationships",
        verbose_name=_("Target Party"),
        help_text=_("The destination/receiving party of the relational connection.")
    )
    relationship_type = models.ForeignKey(
        RelationshipType,
        on_delete=models.PROTECT,
        related_name="party_relationships",
        verbose_name=_("Relationship Type")
    )
    start_date = models.DateField(
        _("Start Date"),
        blank=True, 
        null=True,
        help_text=_("The effective calendar date when this relation officially begins.")
    )
    end_date = models.DateField(
        _("End Date"),
        blank=True, 
        null=True,
        help_text=_("The logical expiration or sunset date of this configuration link.")
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Manually bypass or archive this dependency link without purging history logs.")
    )
    
    class Meta:
        verbose_name = _("Party Relationship")
        verbose_name_plural = _("Party Relationships")
        # Active connections automatically rise to the top of system indexes
        ordering = ["-is_active", "-start_date", "-created"]
        constraints = [
            # Database guardrail: Prevents circular errors by disallowing a Party from relating to itself
            models.CheckConstraint(
                condition=models.Q(source_party=models.F('target_party')),
                name='prevent_self_referential_relationship'
            )
        ]

    def __str__(self):
        return f"{self.source_party} ──[{self.relationship_type}]──> {self.target_party}"