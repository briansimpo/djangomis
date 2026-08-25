from django.contrib.auth import get_user_model
from apps.workflow.models import WorkflowState
from apps.workflow.enums import ActorSource
from apps.workforce.resolvers.workforce_authority import WorkforceAuthority
from apps.workforce.resolvers.workforce_context import WorkforceContext
from apps.workforce.exceptions import WorkerNotFound

User = get_user_model()

class ApproverService:
    
    def get_approvers(self, state: WorkflowState, requester_user=None) -> list:
        resolved_workers = set()
        
        # 1. Establish structural context for relative routing
        requester_worker = None
        if requester_user:
            try:
                requester_worker = WorkforceContext.get_user_worker(requester_user)
            except WorkerNotFound:
                pass

        # 2. Iterate through configured actors
        for actor in state.actors.all():
            
            # Absolute Route: Specific Worker Assigned
            if actor.source == ActorSource.WORKER and actor.worker_id:
                authority = WorkforceAuthority.resolve_worker_authority(actor.worker)
                if authority:
                    resolved_workers.add(authority)
            
            # Absolute Route: Specific Position Assigned
            elif actor.source == ActorSource.POSITION and actor.position_id:
                authorities = WorkforceAuthority.resolve_position_holders(actor.position)
                resolved_workers.update(authorities)
                
            # Absolute Route: Entire Organizational Unit Assigned
            elif actor.source == ActorSource.ORG_UNIT and actor.org_unit_id:
                authorities = WorkforceAuthority.resolve_org_unit_authorities(actor.org_unit)
                resolved_workers.update(authorities)
                
            # Relative Route: Immediate Supervisor
            elif actor.source == ActorSource.SUPERVISOR and requester_worker:
                authority = WorkforceAuthority.resolve_supervisor(requester_worker)
                if authority:
                    resolved_workers.add(authority)
                    
            # Relative Route: N-th Level Approval Chain
            elif actor.source == ActorSource.APPROVAL_CHAIN and requester_worker:
                authority = WorkforceAuthority.resolve_approval_actor(
                    requester_worker, level=actor.level
                )
                if authority:
                    resolved_workers.add(authority)

        # 3. Bridge Back to Django Auth
        return self._map_workers_to_users(resolved_workers)

    def _map_workers_to_users(self, workers: set) -> list:
        final_users = set()
        for worker in workers:
            party = getattr(worker, 'party', None)
            user = getattr(party, 'user', None) if party else None
            
            if user and user.is_active:
                final_users.add(user)
                
        return list(final_users)