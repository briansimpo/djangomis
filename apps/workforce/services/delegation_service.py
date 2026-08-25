from datetime import date
from typing import Optional, Any, List
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from apps.workforce.models import Worker, Delegation, Deployment
from apps.workforce.exceptions import InvalidDelegation,DelegationNotFound


class DelegationValidationService:
    """Handles pure logical checks, system state validations, and cross-node constraints."""

    @classmethod
    def is_delegation_active(cls, delegation: Delegation) -> bool:
        """Validate execution date structures against system state contexts."""
        today = timezone.now().date()
        return delegation.is_active and delegation.start_date <= today <= delegation.end_date

    @classmethod
    def validate_delegation_creation(cls, delegator: Deployment, delegate: Deployment, start_date: date, end_date: date) -> None:
        """Ensures that requested structural overrides meet strict systemic bounds."""
        if delegator.pk == delegate.pk:
            raise InvalidDelegation("Self delegation not allowed.")

        if end_date < start_date:
            raise InvalidDelegation("End date cannot precede start date.")

        if delegator.workstream_id != delegate.workstream_id:
            raise InvalidDelegation("Delegation must occur within the same workstream.")
        

class DelegationQueryService:
    """Handles direct base-level queries and flat data retrieval for authority routing."""

    @classmethod
    def active_delegations_queryset(cls) -> QuerySet[Delegation]:
        """Centralized date logic filters for active delegations."""
        today = timezone.now().date()
        return Delegation.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )

    @classmethod
    def get_active_delegations(cls, deployment: Deployment) -> QuerySet[Delegation]:
        """Delegations issued by deployment."""
        return (
            cls.active_delegations_queryset()
            .select_related("delegate", "delegate__contract", "delegate__contract__worker", "delegated_role")
            .filter(delegator=deployment)
        )

    @classmethod
    def get_received_delegations(cls, deployment: Deployment) -> QuerySet[Delegation]:
        """Delegations received by deployment."""
        return (
            cls.active_delegations_queryset()
            .select_related("delegator", "delegator__contract", "delegator__contract__worker", "delegated_role")
            .filter(delegate=deployment)
        )

    @classmethod
    def get_active_delegation(cls, deployment: Deployment, role: Optional[Any] = None) -> Optional[Delegation]:
        """Return first active delegation matching search parameters."""
        delegations = cls.get_active_delegations(deployment)
        if role:
            delegations = delegations.filter(delegated_role=role)
        return delegations.first()

    @classmethod
    def get_delegation(cls, delegation_id: Any) -> Delegation:
        """Retrieve target context record details."""
        try:
            return Delegation.objects.select_related("delegator", "delegate", "delegated_role").get(pk=delegation_id)
        except Delegation.DoesNotExist:
            raise DelegationNotFound(f"Delegation {delegation_id} not found.")

    @classmethod
    def get_delegation_history(cls, deployment: Deployment) -> QuerySet[Delegation]:
        """Audit log compilation query records execution setup profiles."""
        return (
            Delegation.objects.select_related("delegate", "delegated_role")
            .filter(delegator=deployment)
            .order_by("-start_date")
        )
        

class DelegationWorkflowService:
    """Interprets business routing paths to resolve live operational authorities."""

    @classmethod
    def resolve_delegate(cls, deployment: Deployment, role: Optional[Any] = None) -> Optional[Deployment]:
        """Resolve delegate deployment context target mappings."""
        delegation = DelegationQueryService.get_active_delegation(deployment, role)
        return delegation.delegate if delegation else None

    @classmethod
    def resolve_delegate_worker(cls, deployment: Deployment, role: Optional[Any] = None) -> Optional[Worker]:
        """Resolve precise profile instance for target system operations."""
        delegate = cls.resolve_delegate(deployment, role)
        return delegate.contract.worker if delegate else None

    @classmethod
    def has_active_delegation(cls, deployment: Deployment, role: Optional[Any] = None) -> bool:
        """Determine existence of active operational delegate mapping records."""
        return DelegationQueryService.get_active_delegation(deployment, role) is not None

    @classmethod
    def get_current_delegates(cls, deployment: Deployment) -> List[Deployment]:
        """Return all active delegate target locations mapped structures."""
        return [d.delegate for d in DelegationQueryService.get_active_delegations(deployment)]

    @classmethod
    def get_current_delegate_workers(cls, deployment: Deployment) -> List[Worker]:
        """Return delegated workers details arrays context records mapping setups."""
        return [d.delegate.contract.worker for d in DelegationQueryService.get_active_delegations(deployment)]

    @classmethod
    def resolve_authority_holder(cls, deployment: Deployment, role: Optional[Any] = None) -> Worker:
        """Central delegation-aware authority resolver pipeline logic engine."""
        delegated_worker = cls.resolve_delegate_worker(deployment, role)
        return delegated_worker if delegated_worker else deployment.contract.worker
    

class DelegationMutationService:
    """Executes state changes, revocations, and extensions safely within transactions."""

    @classmethod
    @transaction.atomic
    def delegate(
        cls, delegator: Deployment, delegate: Deployment, delegated_role: Any, 
        start_date: date, end_date: date, reason: Optional[str] = None
    ) -> Delegation:
        DelegationValidationService.validate_delegation_creation(delegator, delegate, start_date, end_date)
        return Delegation.objects.create(
            delegator=delegator, delegate=delegate, delegated_role=delegated_role,
            start_date=start_date, end_date=end_date, reason=reason or "", is_active=True,
        )

    @classmethod
    @transaction.atomic
    def deactivate(cls, delegation: Delegation) -> Delegation:
        delegation.is_active = False
        delegation.save(update_fields=["is_active"])
        return delegation

    @classmethod
    @transaction.atomic
    def extend_delegation(cls, delegation: Delegation, new_end_date: date) -> Delegation:
        if new_end_date < delegation.end_date:
            raise InvalidDelegation("New end date must be later.")
        delegation.end_date = new_end_date
        delegation.save(update_fields=["end_date"])
        return delegation

    @classmethod
    @transaction.atomic
    def activate(cls, delegation: Delegation) -> Delegation:
        delegation.is_active = True
        delegation.save(update_fields=["is_active"])
        return delegation
    
    
class DelegationService:
    """
    Public API Service Facade for Workforce Authority Delegation.

    Preserves historical method names and signatures perfectly to secure 
    backwards-compatibility while delegating complex logic to granular, 
    internal domain modules.
    """
    @classmethod
    def active_delegations_queryset(cls) -> QuerySet[Delegation]:
        return DelegationQueryService.active_delegations_queryset()


    @classmethod
    def is_delegation_active(cls, delegation: Delegation) -> bool:
        return DelegationValidationService.is_delegation_active(delegation)

    @classmethod
    def get_active_delegations(cls, deployment: Deployment) -> QuerySet[Delegation]:
        return DelegationQueryService.get_active_delegations(deployment)

    @classmethod
    def get_received_delegations(cls, deployment: Deployment) -> QuerySet[Delegation]:
        return DelegationQueryService.get_received_delegations(deployment)

    @classmethod
    def get_active_delegation(cls, deployment: Deployment, role: Optional[Any] = None) -> Optional[Delegation]:
        return DelegationQueryService.get_active_delegation(deployment, role)

    @classmethod
    def get_delegation(cls, delegation_id: Any) -> Delegation:
        return DelegationQueryService.get_delegation(delegation_id)

    @classmethod
    def get_delegation_history(cls, deployment: Deployment) -> QuerySet[Delegation]:
        return DelegationQueryService.get_delegation_history(deployment)

    @classmethod
    def resolve_delegate(cls, deployment: Deployment, role: Optional[Any] = None) -> Optional[Deployment]:
        return DelegationWorkflowService.resolve_delegate(deployment, role)

    @classmethod
    def resolve_delegate_worker(cls, deployment: Deployment, role: Optional[Any] = None) -> Optional[Worker]:
        return DelegationWorkflowService.resolve_delegate_worker(deployment, role)

    @classmethod
    def has_active_delegation(cls, deployment: Deployment, role: Optional[Any] = None) -> bool:
        return DelegationWorkflowService.has_active_delegation(deployment, role)

    @classmethod
    def get_current_delegates(cls, deployment: Deployment) -> List[Deployment]:
        return DelegationWorkflowService.get_current_delegates(deployment)

    @classmethod
    def get_current_delegate_workers(cls, deployment: Deployment) -> List[Worker]:
        return DelegationWorkflowService.get_current_delegate_workers(deployment)

    @classmethod
    def resolve_authority_holder(cls, deployment: Deployment, role: Optional[Any] = None) -> Worker:
        return DelegationWorkflowService.resolve_authority_holder(deployment, role)

    @classmethod
    def delegate(
        cls, delegator: Deployment, delegate: Deployment, delegated_role: Any, 
        start_date: date, end_date: date, reason: Optional[str] = None
    ) -> Delegation:
        return DelegationMutationService.delegate(delegator, delegate, delegated_role, start_date, end_date, reason)

    @classmethod
    def deactivate(cls, delegation: Delegation) -> Delegation:
        return DelegationMutationService.deactivate(delegation)

    @classmethod
    def revoke(cls, delegation: Delegation) -> Delegation:
        """Alias route mapped directly to the unified deactivation mechanism."""
        return DelegationMutationService.deactivate(delegation)

    @classmethod
    def extend_delegation(cls, delegation: Delegation, new_end_date: date) -> Delegation:
        return DelegationMutationService.extend_delegation(delegation, new_end_date)

    @classmethod
    def activate(cls, delegation: Delegation) -> Delegation:
        return DelegationMutationService.activate(delegation)
        

