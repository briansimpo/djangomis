from datetime import date
from typing import Optional, Dict, Any
from django.db import transaction
from django.db.models import Q, QuerySet
from apps.workforce.models import Contract, Worker,Placement, Position
from apps.workforce.enums import PlacementStatus, PositionStatus
from apps.workforce.exceptions import (
    InvalidPlacementState,
    PositionAlreadyOccupied,
    PrimaryPlacementExists,
    PlacementNotFound,
)
from .contract_service import ContractService



class PlacementValidationService:
    """Handles pure logical checks, timeline boundary constraints, and state validations."""

    @classmethod
    def is_active(cls, placement: Placement) -> bool:
        """Check if a specific placement instance is functionally active today."""
        today = date.today()
        return (
            placement.status == PlacementStatus.ACTIVE
            and placement.start_date <= today
            and (placement.end_date is None or placement.end_date >= today)
        )

    @classmethod
    def validate_dates(cls, start_date: date, end_date: Optional[date]) -> None:
        """Ensure date boundaries are chronologically sound."""
        if end_date and end_date < start_date:
            raise InvalidPlacementState("End date cannot be before start date.")

    @classmethod
    def validate_position_active(cls, position: Position) -> None:
        """Ensure the target structural slot is available for staffing."""
        if position.status != PositionStatus.ACTIVE:
            raise InvalidPlacementState("Position is not active.")


class PlacementQueryService:
    """Handles optimized base queries, state selectors, and structured record filtration."""

    @classmethod
    def active_placements(cls) -> QuerySet[Placement]:
        today = date.today()
        return Placement.objects.filter(
            status=PlacementStatus.ACTIVE, 
            start_date__lte=today
        ).filter(Q(end_date__isnull=True) | Q(end_date__gte=today))

    @classmethod
    def get_placement(cls, placement_id: Any) -> Placement:
        try:
            return Placement.objects.select_related("position", "contract", "contract__worker").get(pk=placement_id)
        except Placement.DoesNotExist:
            raise PlacementNotFound(f"Placement '{placement_id}' not found.")

    @classmethod
    def get_position_occupants(cls, position: Position, active_only: bool = True) -> QuerySet[Placement]:
        base_qs = cls.active_placements() if active_only else Placement.objects
        return base_qs.select_related("contract", "contract__worker").filter(position=position)

    @classmethod
    def get_position_holder(cls, position: Position) -> Optional[Worker]:
        placement = cls.active_placements().select_related("contract", "contract__worker").filter(position=position, is_primary=True).first()
        return placement.contract.worker if placement else None

    @classmethod
    def get_vacancies(cls, org_unit: Optional[Any] = None) -> QuerySet[Position]:
        occupied_ids = cls.active_placements().filter(is_primary=True).values_list("position_id", flat=True)
        qs = Position.objects.filter(status=PositionStatus.ACTIVE).exclude(id__in=occupied_ids)
        if org_unit:
            qs = qs.filter(org_unit=org_unit)
        return qs

    @classmethod
    def get_worker_placement(cls, worker: Worker) -> Optional[Placement]:
        return cls.active_placements().select_related("position", "contract").filter(contract__worker=worker, is_primary=True).first()

    @classmethod
    def get_worker_position(cls, worker: Worker) -> Optional[Position]:
        placement = cls.get_worker_placement(worker)
        return placement.position if placement else None

    @classmethod
    def get_worker_placements(cls, worker: Worker) -> QuerySet[Placement]:
        return cls.active_placements().select_related("position").filter(contract__worker=worker)

    @classmethod
    def get_worker_placement_history(cls, worker: Worker) -> QuerySet[Placement]:
        return Placement.objects.select_related("position").filter(contract__worker=worker).order_by("-start_date")

    @classmethod
    def get_worker_org_unit(cls, worker: Worker) -> Optional[Any]:
        position = cls.get_worker_position(worker)
        return position.org_unit if position else None
    

class PlacementOccupancyService:
    """Computes operational occupancy metrics and position availability summaries."""

    @classmethod
    def is_position_occupied(cls, position: Position) -> bool:
        return PlacementQueryService.get_position_holder(position) is not None

    @classmethod
    def is_position_vacant(cls, position: Position) -> bool:
        return not cls.is_position_occupied(position)

    @classmethod
    def get_placement_summary(cls, position: Position) -> Dict[str, Any]:
        holder = PlacementQueryService.get_position_holder(position)
        return {
            "position_id": str(position.id),
            "position_code": position.code,
            "position_title": position.title,
            "occupied": holder is not None,
            "vacant": holder is None,
            "holder": holder,
            "occupants_count": PlacementQueryService.get_position_occupants(position).count(),
        }
        

class PlacementMutationService:
    """Executes atomic database writes, lifecycle alterations, and operational transfers."""

    @classmethod
    @transaction.atomic
    def place_worker(
        cls, contract: Contract, position: Position, placement_type: Any,
        start_date: date, is_primary: bool = True, end_date: Optional[date] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Placement:
        ContractService.validate_contract(contract)
        PlacementValidationService.validate_position_active(position)
        PlacementValidationService.validate_dates(start_date, end_date)

        worker = contract.worker
        if is_primary:
            if PlacementQueryService.active_placements().filter(contract__worker=worker, is_primary=True).exists():
                raise PrimaryPlacementExists(f"{worker} already has a primary placement.")
            if PlacementOccupancyService.is_position_occupied(position):
                raise PositionAlreadyOccupied(f"{position} is already occupied.")

        return Placement.objects.create(
            contract=contract, position=position, placement_type=placement_type,
            is_primary=is_primary, status=PlacementStatus.ACTIVE,
            start_date=start_date, end_date=end_date, metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def end_placement(cls, placement: Placement, end_date: date) -> Placement:
        if end_date < placement.start_date:
            raise InvalidPlacementState("End date cannot precede start date.")

        placement.end_date = end_date
        placement.status = PlacementStatus.ENDED
        placement.save(update_fields=["end_date", "status"])
        return placement

    @classmethod
    @transaction.atomic
    def transfer_position(cls, placement: Placement, new_position: Position, transfer_date: date) -> Placement:
        cls.end_placement(placement=placement, end_date=transfer_date)
        return cls.place_worker(
            contract=placement.contract, position=new_position,
            placement_type=placement.placement_type, start_date=transfer_date,
            is_primary=placement.is_primary,
        )

    @classmethod
    @transaction.atomic
    def suspend_placement(cls, placement: Placement) -> Placement:
        placement.status = PlacementStatus.SUSPENDED
        placement.save(update_fields=["status"])
        return placement

    @classmethod
    @transaction.atomic
    def activate_placement(cls, placement: Placement) -> Placement:
        placement.status = PlacementStatus.ACTIVE
        placement.save(update_fields=["status"])
        return placement
    


class PlacementService:
    """
    Public API Service Facade for Organizational Placements.
    
    Preserves historical method names, parameters, and signatures perfectly to 
    secure backwards-compatibility while distributing complexity out to 
    isolated, clean internal domain service components.
    """


    @classmethod
    def is_active(cls, placement: Placement) -> bool:
        return PlacementValidationService.is_active(placement)

    @classmethod
    def active_placements(cls) -> QuerySet[Placement]:
        return PlacementQueryService.active_placements()

    @classmethod
    def get_placement(cls, placement_id: Any) -> Placement:
        return PlacementQueryService.get_placement(placement_id)

    @classmethod
    def get_position_occupants(cls, position: Position, active_only: bool = True) -> QuerySet[Placement]:
        return PlacementQueryService.get_position_occupants(position, active_only)

    @classmethod
    def get_position_holder(cls, position: Position) -> Optional[Worker]:
        return PlacementQueryService.get_position_holder(position)

    @classmethod
    def get_vacancies(cls, org_unit: Optional[Any] = None) -> QuerySet[Position]:
        return PlacementQueryService.get_vacancies(org_unit)

    @classmethod
    def get_worker_placement(cls, worker: Worker) -> Optional[Placement]:
        return PlacementQueryService.get_worker_placement(worker)

    @classmethod
    def get_worker_position(cls, worker: Worker) -> Optional[Position]:
        return PlacementQueryService.get_worker_position(worker)

    @classmethod
    def get_worker_placements(cls, worker: Worker) -> QuerySet[Placement]:
        return PlacementQueryService.get_worker_placements(worker)

    @classmethod
    def get_worker_placement_history(cls, worker: Worker) -> QuerySet[Placement]:
        return PlacementQueryService.get_worker_placement_history(worker)

    @classmethod
    def get_worker_org_unit(cls, worker: Worker) -> Optional[Any]:
        return PlacementQueryService.get_worker_org_unit(worker)

    @classmethod
    def is_position_occupied(cls, position: Position) -> bool:
        return PlacementOccupancyService.is_position_occupied(position)

    @classmethod
    def is_position_vacant(cls, position: Position) -> bool:
        return PlacementOccupancyService.is_position_vacant(position)

    @classmethod
    def get_placement_summary(cls, position: Position) -> Dict[str, Any]:
        return PlacementOccupancyService.get_placement_summary(position)

    @classmethod
    def place_worker(
        cls, contract: Contract, position: Position, placement_type: Any,
        start_date: date, is_primary: bool = True, end_date: Optional[date] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Placement:
        return PlacementMutationService.place_worker(
            contract, position, placement_type, start_date, is_primary, end_date, metadata
        )

    @classmethod
    def end_placement(cls, placement: Placement, end_date: date) -> Placement:
        return PlacementMutationService.end_placement(placement, end_date)

    @classmethod
    def transfer_position(cls, placement: Placement, new_position: Position, transfer_date: date) -> Placement:
        return PlacementMutationService.transfer_position(placement, new_position, transfer_date)

    @classmethod
    def suspend_placement(cls, placement: Placement) -> Placement:
        return PlacementMutationService.suspend_placement(placement)

    @classmethod
    def activate_placement(cls, placement: Placement) -> Placement:
        return PlacementMutationService.activate_placement(placement)