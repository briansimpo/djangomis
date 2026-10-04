from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from djangospice.db.models import BaseModel, OptionModel
from apps.workforce.enums import DeploymentStatus
from .reporting import ReportingType
from .workstreams import Workstream
from .contracts import Contract


class WorkforceRole(OptionModel):
    """
    Look-up dictionary for flexible behavioral capacity tags and transient roles assigned 
    to individuals (e.g., 'Scrum Master', 'Security Reviewer').
    """
    class Meta:
        verbose_name = _("Workforce Role")
        verbose_name_plural = _("Workforce Roles")

    def __str__(self):
        return self.name


class Deployment(BaseModel):
    """
    Maps a Contract (worker agreement) to a specific Workstream, establishing 
    their transient role and tracked capacity in that operational area.
    """
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="deployments",
        verbose_name=_("Associated Contract")
    )
    workstream = models.ForeignKey(
        Workstream,
        on_delete=models.PROTECT,
        related_name="deployments",
        verbose_name=_("Target Workstream")
    )
    role = models.ForeignKey(
        WorkforceRole,
        on_delete=models.PROTECT,
        related_name="deployments",
        verbose_name=_("Behavioral Role")
    )
    percentage = models.DecimalField(
        _("Utilization Allocation (%)"),
        max_digits=5,
        decimal_places=2,
        default=100.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text=_("Resource capacity slice dedicated to this workstream.")
    )
    is_primary = models.BooleanField(
        _("Is Primary Role"),
        default=False,
        help_text=_("Flags if this workstream is the worker's main operational center.")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=DeploymentStatus.choices,
        default=DeploymentStatus.ACTIVE
    )
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(
        _("End Date"),
        null=True,
        blank=True
    )
    metadata = models.JSONField(
        _("Operational Metadata"),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("Deployment")
        verbose_name_plural = _("Deployments")
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gte=F("start_date")),
                name="check_deployment_dates_validity"
            )
        ]

    def __str__(self):
        return f"{self.contract.worker} -> {self.workstream} ({self.role})"


class Supervision(BaseModel):
    """
    Matrix workflow routing graphs establishing transient supervision and reporting 
    vectors strictly within a shared Workstream.
    """
    supervisor = models.ForeignKey(
        Deployment,
        on_delete=models.CASCADE,
        related_name="subordinate_relations", 
        verbose_name=_("Supervisor Assignment")
    )
    subordinate = models.ForeignKey(
        Deployment,
        on_delete=models.CASCADE,
        related_name="supervisor_relations",
        verbose_name=_("Subordinate Assignment")
    )
    reporting_type = models.ForeignKey(
        ReportingType,
        on_delete=models.PROTECT,
        related_name="supervisions",
        verbose_name=_("Supervision Strategy")
    )
  
    class Meta:
        verbose_name = _("Supervision")
        verbose_name_plural = _("Supervisions")
        constraints = [
            models.UniqueConstraint(
                fields=["supervisor", "subordinate", "reporting_type"],
                name="uniq_supervision"
            ),
            models.CheckConstraint(
                condition=Q(supervisor=F('subordinate')),
                name="prevent_self_supervision"
            )
        ]

    def clean(self):
        super().clean()
        if self.supervisor and self.subordinate:
            if self.supervisor.workstream != self.subordinate.workstream:
                raise ValidationError({
                    "subordinate": _("Supervisor and subordinate must be deployed to the same Workstream.")
                })

    def __str__(self):
        return f"[{self.subordinate.workstream}] {self.subordinate.contract.worker} -> {self.supervisor.contract.worker}"


class Delegation(BaseModel):
    """
    Audit log tracking temporary projections of workflow clearance, processing authorizations, 
    and task execution permissions from one performance node to a delegate.
    """
    delegator = models.ForeignKey(
        Deployment,
        on_delete=models.CASCADE,
        related_name="delegations_given",
        verbose_name=_("Delegator")
    )
    delegate = models.ForeignKey(
        Deployment,
        on_delete=models.CASCADE,
        related_name="delegations_received",
        verbose_name=_("Delegate")
    )
    delegated_role = models.ForeignKey(
        WorkforceRole,
        on_delete=models.CASCADE,
        related_name="delegation_instances",
        verbose_name=_("Capability Transferred")
    )
    start_date = models.DateField(_("Activation Date"))
    end_date = models.DateField(_("Expiration Date"))
    reason = models.TextField(_("Justification"), blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Delegation Log")
        verbose_name_plural = _("Delegation Logs")
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(delegator=F('delegate')),
                name="prevent_self_delegation"
            ),
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")),
                name="check_delegation_dates_validity"
            )
        ]

    def __str__(self):
        return f"{self.delegator.contract.worker} delegates to {self.delegate.contract.worker} ({self.delegated_role})"