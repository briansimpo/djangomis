from typing import Optional, List, Any
from apps.workforce.models import Worker, Workstream, Position, Deployment
from apps.workforce.services.contract_service import ContractService
from apps.workforce.services.placement_service import PlacementService
from apps.workforce.services.deployment_service import DeploymentService
from apps.workforce.services.supervision_service import SupervisionService
from apps.workforce.services.delegation_service import DelegationService


class WorkforceResolver:
    """
    Unified workforce read facade. 
    Centralizes resolution logic for workforce hierarchy, assignments, and capacity.
    """

    @classmethod
    def resolve_delegation_or_worker(cls, deployment: Deployment) -> Worker:
        """Helper to resolve the effective worker authority."""
        delegated = DelegationService.resolve_delegate_worker(deployment)
        return delegated if delegated else deployment.contract.worker

    @classmethod
    def get_active_contract(cls, worker: Worker):
        return ContractService.get_worker_contract(worker)

    @classmethod
    def has_active_contract(cls, worker: Worker) -> bool:
        return cls.get_active_contract(worker) is not None

    @classmethod
    def get_primary_placement(cls, worker: Worker):
        return PlacementService.get_worker_placement(worker)

    @classmethod
    def get_primary_position(cls, worker: Worker) -> Optional[Position]:
        return PlacementService.get_worker_position(worker)

    @classmethod
    def get_org_unit(cls, worker: Worker):
        position = cls.get_primary_position(worker)
        return position.org_unit if position else None

    @classmethod
    def get_active_deployments(cls, worker: Worker):
        return DeploymentService.get_active_deployments(worker)

    @classmethod
    def get_primary_deployment(cls, worker: Worker) -> Optional[Deployment]:
        return DeploymentService.get_primary_deployments(worker).first()

    @classmethod
    def get_primary_deployments(cls, worker: Worker):
        return DeploymentService.get_primary_deployments(worker)

    @classmethod
    def get_workstreams(cls, worker: Worker) -> List[Workstream]:
        return DeploymentService.get_worker_workstreams(worker)

    @classmethod
    def get_capacity(cls, worker: Worker):
        return DeploymentService.calculate_capacity(worker)

    @classmethod
    def get_remaining_capacity(cls, worker: Worker):
        return DeploymentService.get_remaining_capacity(worker)

    @classmethod
    def get_supervisor(cls, worker: Worker, reporting_type: Any = None) -> Optional[Worker]:
        deployment = cls.get_primary_deployment(worker)
        if not deployment:
            return None
        
        sup_deployment = SupervisionService.get_direct_supervisor(deployment, reporting_type)
        return cls.resolve_delegation_or_worker(sup_deployment) if sup_deployment else None

    @classmethod
    def get_supervisors(cls, worker: Worker, reporting_type: Any = None) -> List[Worker]:
        deployment = cls.get_primary_deployment(worker)
        if not deployment:
            return []
            
        supervisors = SupervisionService.get_supervisors(deployment, reporting_type)
        return [cls.resolve_delegation_or_worker(s) for s in supervisors]

    @classmethod
    def get_chain_of_command(cls, worker: Worker, reporting_type: Any = None) -> List[Worker]:
        deployment = cls.get_primary_deployment(worker)
        if not deployment:
            return []
            
        chain = SupervisionService.get_supervision_chain(deployment, reporting_type)
        return [cls.resolve_delegation_or_worker(s) for s in chain]

    @classmethod
    def get_subordinates(cls, worker: Worker, reporting_type: Any = None) -> List[Worker]:
        deployment = cls.get_primary_deployment(worker)
        if not deployment:
            return []
        
        subordinates = SupervisionService.get_subordinates(deployment, reporting_type)
        return [s.contract.worker for s in subordinates]

    @classmethod
    def resolve_authority_holder(cls, worker: Worker) -> Worker:
        deployment = cls.get_primary_deployment(worker)
        return cls.resolve_delegation_or_worker(deployment) if deployment else worker

    @classmethod
    def is_member_of_workstream(cls, worker: Worker, workstream: Workstream) -> bool:
        return workstream.pk in [ws.pk for ws in cls.get_workstreams(worker)]

    @classmethod
    def get_workstream_members(cls, workstream: Workstream) -> List[Worker]:
        deployments = DeploymentService.get_workstream_members(workstream)
        return [d.contract.worker for d in deployments]

    @classmethod
    def get_roles(cls, worker: Worker):
        return DeploymentService.get_worker_roles(worker)

    @classmethod
    def occupies_position(cls, worker: Worker, position: Position) -> bool:
        current_pos = cls.get_primary_position(worker)
        return current_pos is not None and current_pos.pk == position.pk