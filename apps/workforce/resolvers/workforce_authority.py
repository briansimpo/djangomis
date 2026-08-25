from typing import Optional, List, Any
from apps.workforce.services.placement_service import PlacementService
from apps.workforce.services.position_service import PositionService
from apps.workforce.services.supervision_service import SupervisionService
from apps.workforce.services.reporting_service import ReportingLineService
from .workforce_resolver import WorkforceResolver

class WorkforceAuthority:
    """
    Enterprise authority resolution engine. 
    Orchestrates resolution across Delegation, Supervision, and Position layers.
    """

    @classmethod
    def _get_sup_actor(cls, deployment, method_name: str, **kwargs):
        """Helper to resolve supervision-based actors with delegation awareness."""
        supervisor = getattr(SupervisionService, method_name)(deployment, **kwargs)
        return WorkforceResolver.resolve_delegation_or_worker(supervisor) if supervisor else None

    @classmethod
    def resolve_position_holder(cls, position) -> Optional[Any]:
        worker = PlacementService.get_position_holder(position)
        return cls.resolve_worker_authority(worker) if worker else None

    @classmethod
    def resolve_position_holders(cls, position) -> List[Any]:
        placements = PlacementService.get_position_occupants(position)
        return [cls.resolve_worker_authority(p.contract.worker) for p in placements]

    @classmethod
    def resolve_worker_authority(cls, worker) -> Any:
        """Returns the effective actor (delegate or worker)."""
        return WorkforceResolver.resolve_authority_holder(worker)

    @classmethod
    def resolve_delegated_authority(cls, worker) -> Any:
        deployment = WorkforceResolver.get_primary_deployment(worker)
        return SupervisionService.DelegationService.resolve_delegate_worker(deployment) if deployment else None

    @classmethod
    def resolve_supervisor(cls, worker, reporting_type=None) -> Any:
        return WorkforceResolver.get_supervisor(worker, reporting_type)

    @classmethod
    def resolve_supervisors(cls, worker, reporting_type=None) -> List[Any]:
        return WorkforceResolver.get_supervisors(worker, reporting_type)

    @classmethod
    def resolve_approval_actor(cls, worker, reporting_type=None, level=1) -> Any:
        deployment = WorkforceResolver.get_primary_deployment(worker)
        if not deployment: return None
        return cls._get_sup_actor(deployment, "resolve_approval_supervisor", level=level, reporting_type=reporting_type)

    @classmethod
    def resolve_escalation_actor(cls, worker, reporting_type=None) -> Any:
        deployment = WorkforceResolver.get_primary_deployment(worker)
        if not deployment: return None
        return cls._get_sup_actor(deployment, "resolve_escalation_supervisor", reporting_type=reporting_type)

    @classmethod
    def resolve_position_supervisor(cls, worker, reporting_type=None) -> Any:
        position = WorkforceResolver.get_primary_position(worker)
        if not position: return None
        sup_pos = ReportingLineService.get_direct_supervisor(position, reporting_type)
        return cls.resolve_position_holder(sup_pos) if sup_pos else None

    @classmethod
    def resolve_position_escalation(cls, worker, reporting_type=None) -> Any:
        position = WorkforceResolver.get_primary_position(worker)
        if not position: return None
        esc_pos = ReportingLineService.get_escalation_position(position, reporting_type)
        return cls.resolve_position_holder(esc_pos) if esc_pos else None

    @classmethod
    def resolve_chain_of_authority(cls, worker, reporting_type=None) -> List[Any]:
        chain = WorkforceResolver.get_chain_of_command(worker, reporting_type)
        return [cls.resolve_worker_authority(item) for item in chain]

    @classmethod
    def resolve_organization_head(cls, worker, reporting_type=None) -> Any:
        chain = cls.resolve_chain_of_authority(worker, reporting_type)
        return chain[-1] if chain else None

    @classmethod
    def resolve_org_unit_authorities(cls, org_unit) -> List[Any]:
        """
        Resolves all active, delegated authority holders 
        within a specific organizational unit.
        """
        # 1. Fetch all active positions bound to this Org Unit
        positions = PositionService.get_positions(org_unit, include_inactive=False)
        
        authorities = []
        # 2. Safely resolve the delegated occupants for each position
        for position in positions:
            authorities.extend(cls.resolve_position_holders(position))
            
        return authorities

    @classmethod
    def resolve_actor(cls, actor_type: str, **kwargs) -> Any:
        mapping = {
            "supervisor": cls.resolve_supervisor,
            "approval": cls.resolve_approval_actor,
            "position_holder": cls.resolve_position_holder,
            "escalation": cls.resolve_escalation_actor,
        }
        if actor_type not in mapping:
            raise ValueError(f"Unknown actor type: {actor_type}")
        return mapping[actor_type](**kwargs)