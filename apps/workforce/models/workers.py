from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice_framework.db.models import BaseModel
from apps.party.models import Party


class Worker(BaseModel):
    """
    The master enterprise identity record representing an active or historic resource. 
    Decouples raw authentication systems and third-party entity details from workforce state tracking.
    """
    party = models.OneToOneField(
        Party,
        on_delete=models.PROTECT,
        related_name="workforce_member",
        verbose_name=_("Party Identity Link"),
        help_text=_("The foundational Legal Entity or Natural Person record associated with this worker.")
    )
   
    worker_number = models.CharField(
        _("Workforce Reference Handle"),
        max_length=100,
        unique=True,
        help_text=_("Unique workforce identifier asset token (e.g., badge number, serial sequence).")
    )
    is_deployable = models.BooleanField(
        _("Is Deployable"),
        default=True,
        help_text=_("Determines if this individual is currently available to accept active operational context workloads.")
    )
    metadata = models.JSONField(
        _("Extensible Member Metadata"),
        default=dict,
        blank=True,
        help_text=_("Flexible schema for schema-less data expansion attributes.")
    )

    class Meta:
        verbose_name = _("Workforce Member")
        verbose_name_plural = _("Workforce Members")
        ordering = ["worker_number"]

    def __str__(self):
        return f"{self.worker_number} - {self.party.name if hasattr(self.party, 'name') else self.party}"

