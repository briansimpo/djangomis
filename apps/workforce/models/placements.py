from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from djangospice.db.models import BaseModel, OptionModel
from apps.workforce.enums import PlacementStatus
from .reporting import Position
from .contracts import Contract

        
class PlacementType(OptionModel):
    """
    Look-up dictionary defining the structural weight or nature of a position's occupancy 
    (e.g., 'Substantive/Permanent', 'Acting Coverage', 'Temporary Overlap').
    """
    class Meta:
        verbose_name = _("Placement Type")
        verbose_name_plural = _("Placement Types")

    def __str__(self):
        return self.name


class Placement(BaseModel):
    """
    The structural staffing connection. Maps a validated worker Contract to an authorized 
    corporate Position on the organizational chart.
    """
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="placements",
        verbose_name=_("Worker Contract")
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="placements",
        verbose_name=_("Occupied Position Slot")
    )
    placement_type = models.ForeignKey(
        PlacementType,
        on_delete=models.PROTECT,
        related_name="placements",
        verbose_name=_("Nature of Occupancy"),
        help_text=_("E.g., Substantive, Acting, Supernumerary/Overlap.")
    )
    is_primary = models.BooleanField(
        _("Is Primary Placement"),
        default=True,
        help_text=_("Flags the worker's main structural home for base HR and payroll routing.")
    )
    status = models.CharField(
        _("Placement Status"),
        max_length=20,
        choices=PlacementStatus.choices,
        default=PlacementStatus.ACTIVE
    )
    start_date = models.DateField(_("Occupancy Start Date"))
    end_date = models.DateField(
        _("Occupancy End Date"),
        null=True,
        blank=True,
        help_text=_("Leave blank for permanent/substantive placements.")
    )
    metadata = models.JSONField(
        _("Placement Metadata"),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("Placement")
        verbose_name_plural = _("Placements")
        ordering = ["-start_date"]
        constraints = [
            # Ensure dates are logical
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gte=F("start_date")),
                name="check_placement_dates_validity"
            ),
            # Prevent the exact same worker from occupying the exact same position 
            # twice simultaneously under the same placement type.
            models.UniqueConstraint(
                fields=["contract", "position", "placement_type", "start_date"],
                name="uniq_placement_instance"
            )
        ]

    def __str__(self):
        return f"{self.contract.worker} -> {self.position.code} ({self.placement_type})"