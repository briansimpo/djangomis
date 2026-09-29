from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice_framework.db.models import BaseModel, OptionModel
from apps.party.models import Party
from apps.workforce.enums import ContractStatus
from apps.workforce.models import Worker


class ContractType(OptionModel):
    """
    Look-up dictionary for the foundational legal classification of a workforce contract 
    (e.g., 'Full-Time Employee', 'Independent Contractor', 'Third-Party Vendor Sourced').
    """
    class Meta:
        verbose_name = _("Engagement Type")
        verbose_name_plural = _("Engagement Types")

    def __str__(self):
        return str(self.name)
  
 
class Contract(BaseModel):
    """
    The governing institutional agreement framework outlining legal, financial, 
    and compliance boundaries between the asset and corporate sponsors.
    """
    worker = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name="contracts",
        verbose_name=_("Workforce Member")
    )
    sponsor_party = models.ForeignKey(
        Party,
        on_delete=models.SET_NULL,
        related_name="sponsored_contracts",
        null=True,
        blank=True,
        verbose_name=_("Sponsoring Legal/Corporate Party")
    )
    contract_type = models.ForeignKey(
        ContractType,
        on_delete=models.SET_NULL,
        related_name="contracts",
        null=True,
        blank=True,
        verbose_name=_("Agreement Categorization")
    )
    status = models.CharField(
        _("Agreement Status"),
        max_length=20,
        choices=ContractStatus.choices,
        default=ContractStatus.ACTIVE
    )
    valid_from = models.DateField(_("Validity Commencement Date"))
    valid_until = models.DateField(
        _("Validity Expiration Date"),
        null=True,
        blank=True
    )
    metadata = models.JSONField(
        _("Agreement Parameters"),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("Contract Agreement")
        verbose_name_plural = _("Contract Agreements")
        ordering = ["-valid_from"]

    def __str__(self):
        return f"ENG-{self.id}: {self.worker} [{self.contract_type}]"
    
  