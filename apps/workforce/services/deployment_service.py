from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.db.models import Q, QuerySet, Sum
from django.utils import timezone
from apps.workforce.models import Deployment, Workstream
from apps.workforce.enums import DeploymentStatus
from apps.workforce.exceptions import InvalidDeploymentState,CapacityExceeded,DeploymentNotFound
from .contract_service import ContractService


class DeploymentValidationService:
    """Handles deep-level parameter checking, boundary rules, and structural date constraints."""

    @classmethod
    def validate_workstream(cls, workstream: Workstream) -> None:
        if not workstream.is_active:
            raise InvalidDeploymentState("Workstream is inactive.")

    @classmethod
    def validate_percentage(cls, percentage: Any) -> Decimal:
        percentage_dec = Decimal(str(percentage))
        if percentage_dec <= 0 or percentage_dec > 100:
            raise InvalidDeploymentState("Deployment percentage must be between 0 and 100.")
        return percentage_dec

    @classmethod
    def validate_dates(cls, start_date: date, end_date: Optional[date]) -> None:
        if end_date and end_date < start_date:
            raise InvalidDeploymentState("End date cannot precede start date.")
        

class DeploymentQueryService:
    """Handles optimized base queries, state selectors, and structured record filtration."""

    @classmethod
    def active_deployment_queryset(cls) -> QuerySet[Deployment]:
        """Base queryset that encapsulates the logic for determining an 'active' deployment."""
        today = timezone.now().date()
        return Deployment.objects.filter(
            status=DeploymentStatus.ACTIVE,
            start_date__lte=today,
        ).filter(Q(end_date__isnull=True) | Q(end_date__gte=today))

    @classmethod
    def get_active_deployments(cls, worker: Any) -> QuerySet[Deployment]:
        return (
            cls.active_deployment_queryset()
            .select_related("workstream", "role", "contract")
            .filter(contract__worker=worker)
            .order_by("-is_primary", "workstream__name")
        )

    @classmethod
    def get_workstream_members(cls, workstream: Workstream) -> QuerySet[Deployment]:
        return (
            cls.active_deployment_queryset()
            .select_related("contract", "contract__worker", "role")
            .filter(workstream=workstream)
        )

    @classmethod
    def get_primary_deployments(cls, worker: Any) -> QuerySet[Deployment]:
        return cls.get_active_deployments(worker).filter(is_primary=True)

    @classmethod
    def get_deployment(cls, deployment_id: Any) -> Deployment:
        try:
            return Deployment.objects.get(pk=deployment_id)
        except Deployment.DoesNotExist:
            raise DeploymentNotFound(f"Deployment {deployment_id} not found.")

    @classmethod
    def get_worker_roles(cls, worker: Any) -> QuerySet:
        return (
            cls.active_deployment_queryset()
            .filter(contract__worker=worker)
            .values_list("role", flat=True)
            .distinct()
        )
        

class DeploymentAnalyticsService:
    """Computes organizational aggregates, available tracking matrices, and workforce statistics."""

    @classmethod
    def calculate_capacity(cls, worker: Any, exclude_deployment_id: Optional[Any] = None) -> Decimal:
        qs = DeploymentQueryService.active_deployment_queryset().filter(contract__worker=worker)
        if exclude_deployment_id:
            qs = qs.exclude(id=exclude_deployment_id)

        result = qs.aggregate(total=Sum("percentage"))
        return result["total"] or Decimal("0.00")

    @classmethod
    def get_remaining_capacity(cls, worker: Any) -> Decimal:
        return Decimal("100.00") - cls.calculate_capacity(worker)

    @classmethod
    def get_workstream_capacity(cls, workstream: Workstream) -> Decimal:
        result = (
            DeploymentQueryService.active_deployment_queryset()
            .filter(workstream=workstream)
            .aggregate(total=Sum("percentage"))
        )
        return result["total"] or Decimal("0.00")

    @classmethod
    def get_worker_workstreams(cls, worker: Any) -> List[Workstream]:
        return [d.workstream for d in DeploymentQueryService.get_active_deployments(worker)]
    

class DeploymentMutationService:
    """Executes atomic writes, state shifts, and bandwidth allocation alterations on deployments."""

    @classmethod
    @transaction.atomic
    def deploy_worker(
        cls, contract: Any, workstream: Workstream, role: Any, percentage: Any,
        start_date: date, is_primary: bool = False, end_date: Optional[date] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Deployment:
        ContractService.validate_contract(contract)
        DeploymentValidationService.validate_workstream(workstream)
        percentage_dec = DeploymentValidationService.validate_percentage(percentage)
        DeploymentValidationService.validate_dates(start_date, end_date)

        current_capacity = DeploymentAnalyticsService.calculate_capacity(contract.worker)
        if current_capacity + percentage_dec > Decimal("100.00"):
            raise CapacityExceeded(
                f"Deployment exceeds available capacity. Current={current_capacity}% Requested={percentage_dec}%"
            )

        return Deployment.objects.create(
            contract=contract, workstream=workstream, role=role, percentage=percentage_dec,
            is_primary=is_primary, status=DeploymentStatus.ACTIVE, start_date=start_date,
            end_date=end_date, metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def end_deployment(cls, deployment: Deployment, end_date: date) -> Deployment:
        if end_date < deployment.start_date:
            raise InvalidDeploymentState("End date cannot precede start date.")

        deployment.end_date = end_date
        deployment.status = DeploymentStatus.ENDED
        deployment.save(update_fields=["end_date", "status"])
        return deployment

    @classmethod
    @transaction.atomic
    def reassign_role(cls, deployment: Deployment, new_role: Any) -> Deployment:
        deployment.role = new_role
        deployment.save(update_fields=["role"])
        return deployment

    @classmethod
    @transaction.atomic
    def change_allocation(cls, deployment: Deployment, new_percentage: Any) -> Deployment:
        new_percentage_dec = Decimal(str(new_percentage))
        consumed_capacity = DeploymentAnalyticsService.calculate_capacity(
            deployment.contract.worker, exclude_deployment_id=deployment.id
        )

        if consumed_capacity + new_percentage_dec > Decimal("100.00"):
            raise CapacityExceeded("Allocation exceeds maximum worker capacity.")

        deployment.percentage = new_percentage_dec
        deployment.save(update_fields=["percentage"])
        return deployment
    

class DeploymentService:
    """
    Public API Service Facade for Worker Deployments.
    
    Preserves historical method names, parameters, and signatures perfectly to 
    secure backwards-compatibility while distributing complexity out to 
    isolated, clean internal domain service components.
    """

    @classmethod
    def active_deployment_queryset(cls) -> QuerySet[Deployment]:
        return DeploymentQueryService.active_deployment_queryset()

    @classmethod
    def get_active_deployments(cls, worker: Any) -> QuerySet[Deployment]:
        return DeploymentQueryService.get_active_deployments(worker)

    @classmethod
    def get_workstream_members(cls, workstream: Workstream) -> QuerySet[Deployment]:
        return DeploymentQueryService.get_workstream_members(workstream)

    @classmethod
    def get_primary_deployments(cls, worker: Any) -> QuerySet[Deployment]:
        return DeploymentQueryService.get_primary_deployments(worker)

    @classmethod
    def get_deployment(cls, deployment_id: Any) -> Deployment:
        return DeploymentQueryService.get_deployment(deployment_id)

    @classmethod
    def get_worker_roles(cls, worker: Any) -> QuerySet:
        return DeploymentQueryService.get_worker_roles(worker)

    @classmethod
    def calculate_capacity(cls, worker: Any, exclude_deployment_id: Optional[Any] = None) -> Decimal:
        return DeploymentAnalyticsService.calculate_capacity(worker, exclude_deployment_id)

    @classmethod
    def get_remaining_capacity(cls, worker: Any) -> Decimal:
        return DeploymentAnalyticsService.get_remaining_capacity(worker)

    @classmethod
    def get_workstream_capacity(cls, workstream: Workstream) -> Decimal:
        return DeploymentAnalyticsService.get_workstream_capacity(workstream)

    @classmethod
    def get_worker_workstreams(cls, worker: Any) -> List[Workstream]:
        return DeploymentAnalyticsService.get_worker_workstreams(worker)

    @classmethod
    def deploy_worker(
        cls, contract: Any, workstream: Workstream, role: Any, percentage: Any,
        start_date: date, is_primary: bool = False, end_date: Optional[date] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Deployment:
        return DeploymentMutationService.deploy_worker(
            contract=contract, workstream=workstream, role=role, percentage=percentage,
            start_date=start_date, is_primary=is_primary, end_date=end_date, metadata=metadata
        )

    @classmethod
    def end_deployment(cls, deployment: Deployment, end_date: date) -> Deployment:
        return DeploymentMutationService.end_deployment(deployment, end_date)

    @classmethod
    def reassign_role(cls, deployment: Deployment, new_role: Any) -> Deployment:
        return DeploymentMutationService.reassign_role(deployment, new_role)

    @classmethod
    def change_allocation(cls, deployment: Deployment, new_percentage: Any) -> Deployment:
        return DeploymentMutationService.change_allocation(deployment, new_percentage)
    
