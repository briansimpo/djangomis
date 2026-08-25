from collections import deque
from typing import Optional, List, Dict, Any, Set
from django.db import transaction
from django.utils import timezone
from apps.workforce.enums import DeploymentStatus
from apps.workforce.models import Deployment, Supervision, Worker
from apps.workforce.exceptions import (
    SupervisionCycleDetected,
    SupervisionNotFound,
    InvalidSupervisionRelationship,
)


class SupervisionQueryService:
    """Handles direct base-level queries for immediate deployment supervision linkages."""

    @classmethod
    def get_supervisors(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        qs = Supervision.objects.select_related(
            "supervisor",
            "supervisor__contract",
            "supervisor__contract__worker",
        ).filter(subordinate=deployment)

        if reporting_type:
            qs = qs.filter(reporting_type=reporting_type)

        return [item.supervisor for item in qs]

    @classmethod
    def get_direct_supervisor(cls, deployment: Deployment, reporting_type: Any = None) -> Optional[Deployment]:
        supervisors = cls.get_supervisors(deployment, reporting_type)
        return supervisors[0] if supervisors else None

    @classmethod
    def get_subordinates(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        qs = Supervision.objects.select_related(
            "subordinate",
            "subordinate__contract",
            "subordinate__contract__worker",
        ).filter(supervisor=deployment)

        if reporting_type:
            qs = qs.filter(reporting_type=reporting_type)

        return [item.subordinate for item in qs]
    

class SupervisionHierarchyService:
    """Manages multi-level recursive paths, loop detection, and workstream tree representations."""

    @classmethod
    def get_supervision_chain(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        qs = Supervision.objects.filter(subordinate__workstream_id=deployment.workstream_id).select_related(
            "supervisor", "supervisor__contract", "supervisor__contract__worker"
        )
        if reporting_type:
            qs = qs.filter(reporting_type=reporting_type)

        sub_to_sup: Dict[int, Deployment] = {}
        for item in qs:
            if item.subordinate_id not in sub_to_sup:
                sub_to_sup[item.subordinate_id] = item.supervisor

        chain: List[Deployment] = []
        current = deployment
        visited: Set[int] = {current.pk}

        while current:
            supervisor = sub_to_sup.get(current.pk)
            if not supervisor:
                break

            if supervisor.pk in visited:
                raise SupervisionCycleDetected("Cycle detected in supervision chain.")

            visited.add(supervisor.pk)
            chain.append(supervisor)
            current = supervisor

        return chain

    @classmethod
    def get_all_subordinates(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        qs = Supervision.objects.filter(supervisor__workstream_id=deployment.workstream_id).select_related(
            "subordinate", "subordinate__contract", "subordinate__contract__worker"
        )
        if reporting_type:
            qs = qs.filter(reporting_type=reporting_type)

        sup_to_subs: Dict[int, List[Deployment]] = {}
        for item in qs:
            sup_to_subs.setdefault(item.supervisor_id, []).append(item.subordinate)

        result: List[Deployment] = []
        queue = deque([deployment])
        visited: Set[int] = set()

        while queue:
            current = queue.popleft()
            if current.pk in visited:
                continue
            visited.add(current.pk)

            children = sup_to_subs.get(current.pk, [])
            for child in children:
                result.append(child)
                queue.append(child)

        return result

    @classmethod
    def validate_no_cycle(cls, supervisor: Deployment, subordinate: Deployment) -> None:
        qs = Supervision.objects.filter(supervisor__workstream_id=supervisor.workstream_id).select_related("subordinate")
        sup_to_subs: Dict[int, List[Deployment]] = {}
        
        for item in qs:
            sup_to_subs.setdefault(item.supervisor_id, []).append(item.subordinate)

        queue = deque([supervisor])
        visited: Set[int] = set()

        while queue:
            current = queue.popleft()
            if current.pk in visited:
                continue
            visited.add(current.pk)

            if current.pk == subordinate.pk:
                raise SupervisionCycleDetected("Cycle detected.")

            children = sup_to_subs.get(current.pk, [])
            for child in children:
                queue.append(child)

    @classmethod
    def reports_to(cls, subordinate: Deployment, supervisor: Deployment, reporting_type: Any = None) -> bool:
        chain = cls.get_supervision_chain(subordinate, reporting_type)
        return any(node.pk == supervisor.pk for node in chain)
    

class SupervisionWorkflowService:
    """Interprets business routing paths for deployment escalations and approvals."""

    @classmethod
    def is_active(cls, deployment: Deployment) -> bool:
        today = timezone.now().date()
        return (
            deployment.status == DeploymentStatus.ACTIVE
            and deployment.start_date <= today
            and (deployment.end_date is None or deployment.end_date >= today)
        )

    @classmethod
    def resolve_escalation_supervisor(cls, deployment: Deployment, reporting_type: Any = None) -> Optional[Deployment]:
        chain = SupervisionHierarchyService.get_supervision_chain(deployment, reporting_type)
        for supervisor in chain:
            if cls.is_active(supervisor):
                return supervisor
        return None

    @classmethod
    def resolve_escalation_worker(cls, deployment: Deployment, reporting_type: Any = None) -> Optional[Worker]:
        supervisor = cls.resolve_escalation_supervisor(deployment, reporting_type)
        return supervisor.contract.worker if supervisor else None

    @classmethod
    def resolve_approval_supervisor(
        cls, deployment: Deployment, level: int = 1, reporting_type: Any = None
    ) -> Optional[Deployment]:
        if level <= 0:
            return deployment

        chain = SupervisionHierarchyService.get_supervision_chain(deployment, reporting_type)
        if len(chain) < level:
            return None

        return chain[level - 1]

    @classmethod
    def resolve_approval_worker(
        cls, deployment: Deployment, level: int = 1, reporting_type: Any = None
    ) -> Optional[Worker]:
        supervisor = cls.resolve_approval_supervisor(deployment, level, reporting_type)
        return supervisor.contract.worker if supervisor else None
    

class SupervisionMutationService:
    """Executes ACID state changes and validations on deployment supervision edges."""

    @classmethod
    @transaction.atomic
    def assign_supervisor(
        cls, supervisor_deployment: Deployment, subordinate_deployment: Deployment, reporting_type: Any
    ) -> Supervision:
        if supervisor_deployment.pk == subordinate_deployment.pk:
            raise InvalidSupervisionRelationship("Self supervision not allowed.")

        if supervisor_deployment.workstream_id != subordinate_deployment.workstream_id:
            raise InvalidSupervisionRelationship("Supervision must remain within same workstream.")

        SupervisionHierarchyService.validate_no_cycle(supervisor_deployment, subordinate_deployment)

        relation, _ = Supervision.objects.get_or_create(
            supervisor=supervisor_deployment,
            subordinate=subordinate_deployment,
            reporting_type=reporting_type,
        )
        return relation

    @classmethod
    @transaction.atomic
    def remove_supervisor(
        cls, supervisor_deployment: Deployment, subordinate_deployment: Deployment, reporting_type: Any
    ) -> None:
        deleted, _ = Supervision.objects.filter(
            supervisor=supervisor_deployment,
            subordinate=subordinate_deployment,
            reporting_type=reporting_type,
        ).delete()

        if not deleted:
            raise SupervisionNotFound("Supervision relationship not found.")
      

class SupervisionService:
    """
    Public API Service Facade for Operational Reporting Hierarchy.
    
    Preserves historical method names and signatures perfectly to secure 
    backwards-compatibility across the codebase while delegating complex 
    logic to granular, internal domain modules.
    """


    @classmethod
    def get_supervisors(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        return SupervisionQueryService.get_supervisors(deployment, reporting_type)

    @classmethod
    def get_direct_supervisor(cls, deployment: Deployment, reporting_type: Any = None) -> Optional[Deployment]:
        return SupervisionQueryService.get_direct_supervisor(deployment, reporting_type)

    @classmethod
    def get_subordinates(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        return SupervisionQueryService.get_subordinates(deployment, reporting_type)

    @classmethod
    def get_supervision_chain(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        return SupervisionHierarchyService.get_supervision_chain(deployment, reporting_type)

    @classmethod
    def get_all_subordinates(cls, deployment: Deployment, reporting_type: Any = None) -> List[Deployment]:
        return SupervisionHierarchyService.get_all_subordinates(deployment, reporting_type)

    @classmethod
    def reports_to(cls, subordinate: Deployment, supervisor: Deployment, reporting_type: Any = None) -> bool:
        return SupervisionHierarchyService.reports_to(subordinate, supervisor, reporting_type)

    @classmethod
    def validate_no_cycle(cls, supervisor: Deployment, subordinate: Deployment) -> None:
        SupervisionHierarchyService.validate_no_cycle(supervisor, subordinate)

    @classmethod
    def resolve_escalation_supervisor(cls, deployment: Deployment, reporting_type: Any = None) -> Optional[Deployment]:
        return SupervisionWorkflowService.resolve_escalation_supervisor(deployment, reporting_type)

    @classmethod
    def resolve_escalation_worker(cls, deployment: Deployment, reporting_type: Any = None) -> Optional[Worker]:
        return SupervisionWorkflowService.resolve_escalation_worker(deployment, reporting_type)

    @classmethod
    def resolve_approval_supervisor(
        cls, deployment: Deployment, level: int = 1, reporting_type: Any = None
    ) -> Optional[Deployment]:
        return SupervisionWorkflowService.resolve_approval_supervisor(deployment, level, reporting_type)

    @classmethod
    def resolve_approval_worker(
        cls, deployment: Deployment, level: int = 1, reporting_type: Any = None
    ) -> Optional[Worker]:
        return SupervisionWorkflowService.resolve_approval_worker(deployment, level, reporting_type)

    @classmethod
    def is_active(cls, deployment: Deployment) -> bool:
        return SupervisionWorkflowService.is_active(deployment)


    @classmethod
    def assign_supervisor(
        cls, supervisor_deployment: Deployment, subordinate_deployment: Deployment, reporting_type: Any
    ) -> Supervision:
        return SupervisionMutationService.assign_supervisor(
            supervisor_deployment, subordinate_deployment, reporting_type
        )

    @classmethod
    def remove_supervisor(
        cls, supervisor_deployment: Deployment, subordinate_deployment: Deployment, reporting_type: Any
    ) -> None:
        SupervisionMutationService.remove_supervisor(
            supervisor_deployment, subordinate_deployment, reporting_type
        )