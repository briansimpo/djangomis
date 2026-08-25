from typing import Optional, Dict, Any
from django.db import transaction
from django.db.models import QuerySet, Q

from apps.workforce.models import Position
from apps.workforce.enums import PositionStatus
from apps.workforce.exceptions import (
    PositionNotFound,
    DuplicatePosition,
    InvalidPositionState,
)


class PositionValidationService:
    """Handles domain-specific logic, state transition rules, and staffing viability."""

    @classmethod
    def validate_reactivation(cls, position: Position) -> None:
        if position.status == PositionStatus.ABOLISHED:
            raise InvalidPositionState("An abolished position cannot be reactivated.")

    @classmethod
    def validate_suspendable(cls, position: Position) -> None:
        if position.status == PositionStatus.ABOLISHED:
            raise InvalidPositionState("Cannot suspend an abolished position.")

    @classmethod
    def is_staffable(cls, position: Position) -> bool:
        return position.status == PositionStatus.ACTIVE
    

class PositionQueryService:
    """Handles database read operations, multi-filter search, and relationship hydration."""

    @classmethod
    def get_position(cls, position_id: Any) -> Position:
        try:
            return Position.objects.select_related("org_unit", "position_type").get(pk=position_id)
        except Position.DoesNotExist:
            raise PositionNotFound(f"Position '{position_id}' does not exist.")

    @classmethod
    def get_positions(cls, org_unit: Any, include_inactive: bool = True) -> QuerySet[Position]:
        qs = Position.objects.select_related("org_unit", "position_type").filter(org_unit=org_unit)
        if not include_inactive:
            qs = qs.filter(status=PositionStatus.ACTIVE)
        return qs.order_by("code")

    @classmethod
    def get_active_positions(cls) -> QuerySet[Position]:
        return Position.objects.select_related("org_unit", "position_type").filter(status=PositionStatus.ACTIVE).order_by("code")

    @classmethod
    def search_positions(cls, query: Optional[str] = None, org_unit: Optional[Any] = None, 
                         position_type: Optional[Any] = None, status: Optional[str] = None) -> QuerySet[Position]:
        qs = Position.objects.select_related("org_unit", "position_type")
        if query:
            qs = qs.filter(Q(code__icontains=query) | Q(title__icontains=query))
        if org_unit:
            qs = qs.filter(org_unit=org_unit)
        if position_type:
            qs = qs.filter(position_type=position_type)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("code")
    

class PositionMutationService:
    """Executes state-mutating transactions on position records."""

    @classmethod
    @transaction.atomic
    def create_position(cls, org_unit: Any, code: str, title: str, 
                        position_type: Any, metadata: Optional[Dict[str, Any]] = None) -> Position:
        code = code.strip()
        if Position.objects.filter(code=code).exists():
            raise DuplicatePosition(f"Position with code '{code}' already exists.")

        return Position.objects.create(
            org_unit=org_unit, code=code, title=title, position_type=position_type,
            status=PositionStatus.ACTIVE, metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def activate_position(cls, position: Position) -> Position:
        if position.status == PositionStatus.ACTIVE:
            return position
        PositionValidationService.validate_reactivation(position)
        
        position.status = PositionStatus.ACTIVE
        position.save(update_fields=["status", "updated"])
        return position

    @classmethod
    @transaction.atomic
    def suspend_position(cls, position: Position) -> Position:
        PositionValidationService.validate_suspendable(position)
        if position.status == PositionStatus.SUSPENDED:
            return position

        position.status = PositionStatus.SUSPENDED
        position.save(update_fields=["status", "updated"])
        return position

    @classmethod
    @transaction.atomic
    def abolish_position(cls, position: Position) -> Position:
        if position.status == PositionStatus.ABOLISHED:
            return position

        position.status = PositionStatus.ABOLISHED
        position.save(update_fields=["status", "updated"])
        return position
    

class PositionService:
    """Public API Facade for Position Management."""

    @classmethod
    def get_position(cls, position_id: Any) -> Position:
        return PositionQueryService.get_position(position_id)

    @classmethod
    def get_positions(cls, org_unit: Any, include_inactive: bool = True) -> QuerySet[Position]:
        return PositionQueryService.get_positions(org_unit, include_inactive)

    @classmethod
    def get_active_positions(cls) -> QuerySet[Position]:
        return PositionQueryService.get_active_positions()

    @classmethod
    def search_positions(cls, query: Optional[str] = None, org_unit: Optional[Any] = None, position_type: Optional[Any] = None, status: Optional[str] = None) -> QuerySet[Position]:
        return PositionQueryService.search_positions(query, org_unit, position_type, status)

    @classmethod
    def is_staffable(cls, position: Position) -> bool:
        return PositionValidationService.is_staffable(position)

    @classmethod
    def create_position(cls, org_unit: Any, code: str, title: str, 
                        position_type: Any, metadata: Optional[Dict[str, Any]] = None) -> Position:
        return PositionMutationService.create_position(org_unit, code, title, position_type, metadata)

    @classmethod
    def activate_position(cls, position: Position) -> Position:
        return PositionMutationService.activate_position(position)

    @classmethod
    def suspend_position(cls, position: Position) -> Position:
        return PositionMutationService.suspend_position(position)

    @classmethod
    def abolish_position(cls, position: Position) -> Position:
        return PositionMutationService.abolish_position(position)