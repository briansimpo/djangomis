from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice_framework.db.models import BaseModel, OptionModel
from apps.organization.models import OrgUnit
from apps.workforce.enums import PositionStatus


class PositionType(OptionModel):
    """
    Look-up dictionary for structural grading, role archetypes, or functional competency 
    clusters (e.g., 'Executive', 'Senior Engineer', 'General Staff').
    """
    class Meta:
        verbose_name = _("Position Type")
        verbose_name_plural = _("Position Types")

    def __str__(self):
        return self.name
 

class Position(BaseModel):
    """
    A structural container representing an authorized organizational resource allocation slot. 
    Maintains standalone validity independent of personnel staffing.
    """
    org_unit = models.ForeignKey(
        OrgUnit,
        on_delete=models.PROTECT,
        related_name="positions",
        verbose_name=_("Hosting Org Unit"),
        help_text=_("The cost-center or department where this position resides.")
    )
    code = models.CharField(
        _("Position Code"),
        max_length=100,
        unique=True,
        help_text=_("Systemic corporate key indexing this role.")
    )
    title = models.CharField(
        _("Position Title"),
        max_length=255,
        help_text=_("The official localized name for the business role.")
    )
    position_type = models.ForeignKey(
        PositionType,
        on_delete=models.PROTECT,
        related_name="positions",
        verbose_name=_("Position Type"),
        help_text=_("The structural classification framing this position.")
    )
    status = models.CharField(
        _("Position State"),
        max_length=20,
        choices=PositionStatus.choices,
        default=PositionStatus.ACTIVE,
        help_text=_("Governs hiring eligibility and budget availability.")
    )
    metadata = models.JSONField(
        _("Extensible Metadata"),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.title} ({self.org_unit})"

