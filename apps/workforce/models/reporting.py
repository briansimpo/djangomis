from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _
from djangospice.db.models import BaseModel, OptionModel
from .positions import Position

    
class ReportingType(OptionModel):
    """
    Look-up dictionary specifying structural authority frameworks and escalation tracks 
    (e.g., 'Administrative/Line', 'Functional/Matrix').
    """
    class Meta:
        verbose_name = _("Reporting Type")
        verbose_name_plural = _("Reporting Types")     

    def __str__(self):
        return self.name


class ReportingLine(BaseModel):
    """
    Persistent structural hierarchy linking authoritative reporting channels directly 
    between Positions, independent of individual human assignments.
    """
    supervisor = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="subordinate_lines",
        verbose_name=_("Supervisor Position")
    )
    subordinate = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="supervisor_lines",
        verbose_name=_("Subordinate Position")
    )
    reporting_type = models.ForeignKey(
        ReportingType,
        on_delete=models.PROTECT,
        related_name="reporting_lines",
        verbose_name=_("Reporting Classification")
    )

    class Meta:
        verbose_name = _("Reporting Line")
        verbose_name_plural = _("Reporting Lines")
        constraints = [
            models.UniqueConstraint(
                fields=["supervisor", "subordinate", "reporting_type"],
                name="uniq_reporting_line"
            ),
            models.CheckConstraint(
                check=~Q(supervisor=F('subordinate')),
                name="prevent_self_reporting"
            )
        ]

    def __str__(self):
        return f"{self.subordinate.code} --[{self.reporting_type}]--> {self.supervisor.code}"