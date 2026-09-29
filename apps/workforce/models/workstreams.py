from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice_framework.db.models import BaseModel, OptionModel


class WorkstreamType(OptionModel):
    """
    Look-up dictionary categorizing the operational nature of the hub 
    (e.g., 'Agile Pod', 'Steering Committee', 'Incident Task Force').
    """
    class Meta:
        verbose_name = _("Workstream Type")
        verbose_name_plural = _("Workstream Types")

    def __str__(self):
        return self.name


class Workstream(BaseModel):
    """
    A concrete, authoritative container managed exclusively by the workforce engine. 
    It defines an operational group or execution hub. Other business modules link TO 
    this entity to leverage its defined workforce (Deployments & Supervisions).
    """
    name = models.CharField(
        _("Workstream Name"),
        max_length=255,
        help_text=_("The official human-readable namespace for this operational group.")
    )
    workstream_type = models.ForeignKey(
        WorkstreamType,
        on_delete=models.PROTECT,
        related_name="workstreams",
        verbose_name=_("Hub Classification")
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("Parent Workstream")
    )
    is_active = models.BooleanField(
        _("Is Active Hub"),
        default=True,
        help_text=_("Governs whether this workstream can accept new worker Deployments.")
    )
    metadata = models.JSONField(
        _("Operational Metadata"),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("Workstream")
        verbose_name_plural = _("Workstreams")
        ordering = ["name"]

    def __str__(self):
        return self.name
    