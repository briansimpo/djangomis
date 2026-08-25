from typing import Optional, List, Dict, Any, Set
from collections import deque
from django.db import transaction
from django.db.models import QuerySet, Q
from apps.workforce.models import Position, ReportingLine
from apps.workforce.exceptions import ReportingCycleDetected, ReportingLineNotFound, ReportingLineExists
from .placement_service import PlacementService


class ReportingQueryService:
    """Handles direct base-level queries and flat data retrieval from the database."""
    
    @classmethod
    def get_related_positions(
        cls, lookup_field: str, select_field: str, position: Position, reporting_type: Optional[Any] = None
    ) -> List[Position]:
        filters = {lookup_field: position}
        if reporting_type:
            filters["reporting_type"] = reporting_type
        
        qs = ReportingLine.objects.select_related(select_field).filter(**filters)
        return [getattr(line, select_field) for line in qs]

    @classmethod
    def get_supervisors(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return cls.get_related_positions("subordinate", "supervisor", position, reporting_type)

    @classmethod
    def get_subordinates(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return cls.get_related_positions("supervisor", "subordinate", position, reporting_type)

    @classmethod
    def get_direct_supervisor(cls, position: Position, reporting_type: Optional[Any] = None) -> Optional[Position]:
        supervisors = cls.get_supervisors(position, reporting_type)
        return supervisors[0] if supervisors else None

    @classmethod
    def get_reporting_line(
        cls, subordinate: Position, supervisor: Position, reporting_type: Optional[Any] = None
    ) -> Optional[ReportingLine]:
        qs = ReportingLine.objects.filter(subordinate=subordinate, supervisor=supervisor)
        if reporting_type:
            qs = qs.filter(reporting_type=reporting_type)
        return qs.first()

    @classmethod
    def get_span_of_control(cls, position: Position, reporting_type: Optional[Any] = None) -> int:
        filters = {"supervisor": position}
        if reporting_type:
            filters["reporting_type"] = reporting_type
        return ReportingLine.objects.filter(**filters).count()

    @classmethod
    def get_root_positions(cls) -> QuerySet[Position]:
        subordinate_ids = ReportingLine.objects.values_list("subordinate_id", flat=True)
        return Position.objects.exclude(id__in=subordinate_ids)
    
    
class ReportingHierarchyService:
    """Manages multi-level recursive paths, loop detection, and tree representations using single-query performance strategies."""

    @classmethod
    def _build_reporting_maps(cls, reporting_type: Optional[Any] = None) -> tuple[Dict[int, int], Dict[int, List[Position]]]:
        filters = {}
        if reporting_type:
            filters["reporting_type"] = reporting_type
            
        lines = ReportingLine.objects.select_related("subordinate", "supervisor").filter(**filters)
        sub_to_sup: Dict[int, int] = {}
        sup_to_subs: Dict[int, List[Position]] = {}
        
        for line in lines:
            sub_to_sup[line.subordinate_id] = line.supervisor_id
            sup_to_subs.setdefault(line.supervisor_id, []).append(line.subordinate)
            
        return sub_to_sup, sup_to_subs

    @classmethod
    def get_chain_of_command(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        filters = {"reporting_type": reporting_type} if reporting_type else {}
        lines = ReportingLine.objects.filter(**filters).values_list("subordinate_id", "supervisor_id")
        sub_to_sup = dict(lines)
        
        if not sub_to_sup:
            return []
            
        current_id = position.id
        visited: Set[int] = set()
        supervisor_ids_to_fetch: List[int] = []

        while current_id in sub_to_sup:
            sup_id = sub_to_sup[current_id]
            if sup_id in visited:
                raise ReportingCycleDetected("Hierarchy cycle detected during traversal.")
            visited.add(sup_id)
            supervisor_ids_to_fetch.append(sup_id)
            current_id = sup_id

        positions_map = {p.id: p for p in Position.objects.filter(id__in=supervisor_ids_to_fetch)}
        return [positions_map[sid] for sid in supervisor_ids_to_fetch if sid in positions_map]

    @classmethod
    def get_all_subordinates(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        _, sup_to_subs = cls._build_reporting_maps(reporting_type)
        results: List[Position] = []
        queue = deque([position.id])
        visited: Set[int] = set()

        while queue:
            current_id = queue.popleft()
            if current_id in visited:
                continue
            visited.add(current_id)
            
            for child in sup_to_subs.get(current_id, []):
                results.append(child)
                queue.append(child.id)
        return results

    @classmethod
    def validate_no_cycle(cls, supervisor: Position, subordinate: Position) -> None:
        if supervisor.id == subordinate.id:
            raise ReportingCycleDetected("A position cannot report to itself.")
        chain_ids = {p.id for p in cls.get_chain_of_command(supervisor)}
        if subordinate.id in chain_ids:
            raise ReportingCycleDetected("Reporting hierarchy cycle detected.")

    @classmethod
    def get_top_leader(cls, position: Position, reporting_type: Optional[Any] = None) -> Position:
        chain = cls.get_chain_of_command(position, reporting_type)
        return chain[-1] if chain else position

    @classmethod
    def get_reporting_path(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return [position] + cls.get_chain_of_command(position, reporting_type)

    @classmethod
    def get_org_chart(cls, root_position: Position, reporting_type: Optional[Any] = None) -> Dict[str, Any]:
        _, sup_to_subs = cls._build_reporting_maps(reporting_type)

        def _build_node(pos: Position) -> Dict[str, Any]:
            return {
                "position": pos,
                "children": [_build_node(child) for child in sup_to_subs.get(pos.id, [])]
            }
        return _build_node(root_position)

    @classmethod
    def get_max_depth(cls, root_position: Position, reporting_type: Optional[Any] = None) -> int:
        _, sup_to_subs = cls._build_reporting_maps(reporting_type)

        def _compute_depth(pos_id: int) -> int:
            children = sup_to_subs.get(pos_id, [])
            if not children:
                return 0
            return 1 + max(_compute_depth(child.id) for child in children)
        return _compute_depth(root_position.id)

    @classmethod
    def get_hierarchy_statistics(cls, root_position: Position, reporting_type: Optional[Any] = None) -> Dict[str, Any]:
        _, sup_to_subs = cls._build_reporting_maps(reporting_type)
        descendants_count = 0
        max_depth = 0
        queue = deque([(root_position.id, 0)])
        
        while queue:
            curr_id, curr_depth = queue.popleft()
            if curr_depth > max_depth:
                max_depth = curr_depth
            children = sup_to_subs.get(curr_id, [])
            descendants_count += len(children)
            for child in children:
                queue.append((child.id, curr_depth + 1))

        return {
            "root": root_position,
            "total_positions": descendants_count + 1,
            "depth": max_depth,
            "span_of_control": len(sup_to_subs.get(root_position.id, [])),
        }


class ReportingWorkflowService:
    """Interprets business routing paths for automated workforce escalation workflows."""

    @classmethod
    def get_approval_position(
        cls, requester_position: Position, level: int = 1, reporting_type: Optional[Any] = None
    ) -> Optional[Position]:
        if level <= 0:
            return requester_position
        chain = ReportingHierarchyService.get_chain_of_command(requester_position, reporting_type)
        return chain[level - 1] if len(chain) >= level else None

    @classmethod
    def get_approval_holder(
        cls, requester_position: Position, level: int = 1, reporting_type: Optional[Any] = None
    ) -> Optional[Any]:
        position = cls.get_approval_position(requester_position, level, reporting_type)
        return PlacementService.get_position_holder(position) if position else None

    @classmethod
    def get_escalation_position(cls, position: Position, reporting_type: Optional[Any] = None) -> Optional[Position]:
        chain = ReportingHierarchyService.get_chain_of_command(position, reporting_type)
        for supervisor in chain:
            if not PlacementService.is_position_vacant(supervisor):
                return supervisor
        return None

    @classmethod
    def get_active_approver(
        cls, requester_position: Position, level: int = 1, reporting_type: Optional[Any] = None
    ) -> Optional[Any]:
        chain = ReportingHierarchyService.get_chain_of_command(requester_position, reporting_type)
        active_chain = chain[level - 1:] if len(chain) >= level else []
        
        for supervisor in active_chain:
            holder = PlacementService.get_position_holder(supervisor)
            if holder:
                return holder
        return None

    @classmethod
    def get_vacant_supervisors(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        chain = ReportingHierarchyService.get_chain_of_command(position, reporting_type)
        return [sup for sup in chain if PlacementService.is_position_vacant(sup)]
    
    
class ReportingMutationService:
    """Executes ACID state changes and bulk array mutations on relationship edges."""

    @classmethod
    @transaction.atomic
    def assign_supervisor(cls, subordinate: Position, supervisor: Position, reporting_type: Any) -> ReportingLine:
        ReportingHierarchyService.validate_no_cycle(supervisor, subordinate)
        if ReportingQueryService.get_reporting_line(subordinate, supervisor, reporting_type):
            raise ReportingLineExists("Reporting relationship already exists.")
        return ReportingLine.objects.create(
            supervisor=supervisor, subordinate=subordinate, reporting_type=reporting_type
        )

    @classmethod
    @transaction.atomic
    def remove_supervisor(cls, subordinate: Position, supervisor: Position, reporting_type: Any) -> None:
        deleted, _ = ReportingLine.objects.filter(
            supervisor=supervisor, subordinate=subordinate, reporting_type=reporting_type
        ).delete()
        if not deleted:
            raise ReportingLineNotFound("Reporting relationship not found.")

    @classmethod
    @transaction.atomic
    def replace_supervisor(cls, subordinate: Position, old_sup: Position, new_sup: Position, reporting_type: Any) -> ReportingLine:
        cls.remove_supervisor(subordinate, old_sup, reporting_type)
        return cls.assign_supervisor(subordinate, new_sup, reporting_type)

    @classmethod
    @transaction.atomic
    def reassign_subordinates(cls, from_sup: Position, to_sup: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        subordinates = ReportingQueryService.get_subordinates(from_sup, reporting_type)
        if not subordinates:
            return []
        filters = {"supervisor": from_sup, "subordinate__in": subordinates}
        if reporting_type:
            filters["reporting_type"] = reporting_type
            
        ReportingLine.objects.filter(**filters).update(supervisor=to_sup)
        return subordinates

    @classmethod
    @transaction.atomic
    def move_subtree(cls, root_position: Position, new_supervisor: Position, reporting_type: Any) -> ReportingLine:
        current_supervisor = ReportingQueryService.get_direct_supervisor(root_position, reporting_type)
        if current_supervisor:
            cls.remove_supervisor(root_position, current_supervisor, reporting_type)
        return cls.assign_supervisor(root_position, new_supervisor, reporting_type)

    @classmethod
    @transaction.atomic
    def bulk_assign_supervisors(cls, relationships: List[Dict[str, Any]]) -> List[ReportingLine]:
        lines_to_create = []
        for r in relationships:
            ReportingHierarchyService.validate_no_cycle(r["supervisor"], r["subordinate"])
            lines_to_create.append(
                ReportingLine(
                    subordinate=r["subordinate"], supervisor=r["supervisor"], reporting_type=r["reporting_type"]
                )
            )
        return ReportingLine.objects.bulk_create(lines_to_create)

    @classmethod
    @transaction.atomic
    def bulk_remove_supervisors(cls, relationships: List[Dict[str, Any]]) -> None:
        if not relationships:
            return
        q_lookup = Q()
        for r in relationships:
            q_lookup |= Q(subordinate=r["subordinate"], supervisor=r["supervisor"], reporting_type=r["reporting_type"])
        ReportingLine.objects.filter(q_lookup).delete()
        

class ReportingLineService:
    """
    Public API Service Facade.
    
    Preserves historical method names and signatures perfectly to secure 
    backwards-compatibility across all dependency layers.
    """

    @classmethod
    def get_related_positions(
        cls, lookup_field: str, select_field: str, position: Position, reporting_type: Optional[Any] = None
    ) -> List[Position]:
        return ReportingQueryService.get_related_positions(lookup_field, select_field, position, reporting_type)

    @classmethod
    def get_supervisors(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return ReportingQueryService.get_supervisors(position, reporting_type)

    @classmethod
    def get_subordinates(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return ReportingQueryService.get_subordinates(position, reporting_type)

    @classmethod
    def get_direct_supervisor(cls, position: Position, reporting_type: Optional[Any] = None) -> Optional[Position]:
        return ReportingQueryService.get_direct_supervisor(position, reporting_type)

    @classmethod
    def get_reporting_line(
        cls, subordinate: Position, supervisor: Position, reporting_type: Optional[Any] = None
    ) -> Optional[ReportingLine]:
        return ReportingQueryService.get_reporting_line(subordinate, supervisor, reporting_type)

    @classmethod
    def get_span_of_control(cls, position: Position, reporting_type: Optional[Any] = None) -> int:
        return ReportingQueryService.get_span_of_control(position, reporting_type)

    @classmethod
    def get_root_positions(cls) -> QuerySet[Position]:
        return ReportingQueryService.get_root_positions()

    @classmethod
    def validate_no_cycle(cls, supervisor: Position, subordinate: Position) -> None:
        ReportingHierarchyService.validate_no_cycle(supervisor, subordinate)

    @classmethod
    def get_chain_of_command(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return ReportingHierarchyService.get_chain_of_command(position, reporting_type)

    @classmethod
    def get_all_subordinates(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return ReportingHierarchyService.get_all_subordinates(position, reporting_type)

    @classmethod
    def get_top_leader(cls, position: Position, reporting_type: Optional[Any] = None) -> Position:
        return ReportingHierarchyService.get_top_leader(position, reporting_type)

    @classmethod
    def get_reporting_path(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return ReportingHierarchyService.get_reporting_path(position, reporting_type)

    @classmethod
    def get_org_chart(cls, root_position: Position, reporting_type: Optional[Any] = None) -> Dict[str, Any]:
        return ReportingHierarchyService.get_org_chart(root_position, reporting_type)

    @classmethod
    def get_max_depth(cls, root_position: Position, reporting_type: Optional[Any] = None) -> int:
        return ReportingHierarchyService.get_max_depth(root_position, reporting_type)

    @classmethod
    def get_hierarchy_statistics(cls, root_position: Position, reporting_type: Optional[Any] = None) -> Dict[str, Any]:
        return ReportingHierarchyService.get_hierarchy_statistics(root_position, reporting_type)

    @classmethod
    def get_approval_position(
        cls, requester_position: Position, level: int = 1, reporting_type: Optional[Any] = None
    ) -> Optional[Position]:
        return ReportingWorkflowService.get_approval_position(requester_position, level, reporting_type)

    @classmethod
    def get_approval_holder(
        cls, requester_position: Position, level: int = 1, reporting_type: Optional[Any] = None
    ) -> Optional[Any]:
        return ReportingWorkflowService.get_approval_holder(requester_position, level, reporting_type)

    @classmethod
    def get_escalation_position(cls, position: Position, reporting_type: Optional[Any] = None) -> Optional[Position]:
        return ReportingWorkflowService.get_escalation_position(position, reporting_type)

    @classmethod
    def get_active_approver(
        cls, requester_position: Position, level: int = 1, reporting_type: Optional[Any] = None
    ) -> Optional[Any]:
        return ReportingWorkflowService.get_active_approver(requester_position, level, reporting_type)

    @classmethod
    def get_vacant_supervisors(cls, position: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return ReportingWorkflowService.get_vacant_supervisors(position, reporting_type)

    @classmethod
    def assign_supervisor(cls, subordinate: Position, supervisor: Position, reporting_type: Any) -> ReportingLine:
        return ReportingMutationService.assign_supervisor(subordinate, supervisor, reporting_type)

    @classmethod
    def remove_supervisor(cls, subordinate: Position, supervisor: Position, reporting_type: Any) -> None:
        ReportingMutationService.remove_supervisor(subordinate, supervisor, reporting_type)

    @classmethod
    def replace_supervisor(cls, subordinate: Position, old_sup: Position, new_sup: Position, reporting_type: Any) -> ReportingLine:
        return ReportingMutationService.replace_supervisor(subordinate, old_sup, new_sup, reporting_type)

    @classmethod
    def reassign_subordinates(cls, from_sup: Position, to_sup: Position, reporting_type: Optional[Any] = None) -> List[Position]:
        return ReportingMutationService.reassign_subordinates(from_sup, to_sup, reporting_type)

    @classmethod
    def move_subtree(cls, root_position: Position, new_supervisor: Position, reporting_type: Any) -> ReportingLine:
        return ReportingMutationService.move_subtree(root_position, new_supervisor, reporting_type)

    @classmethod
    def bulk_assign_supervisors(cls, relationships: List[Dict[str, Any]]) -> List[ReportingLine]:
        return ReportingMutationService.bulk_assign_supervisors(relationships)

    @classmethod
    def bulk_remove_supervisors(cls, relationships: List[Dict[str, Any]]) -> None:
        ReportingMutationService.bulk_remove_supervisors(relationships)