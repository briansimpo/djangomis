from typing import Any
from dataclasses import dataclass
from typing import Optional, Any
from apps.workforce.exceptions import WorkerNotFound
from .workforce_resolver import WorkforceResolver
from .workforce_authority import WorkforceAuthority


@dataclass
class WorkforceContextData:
    """
    A strictly typed data structure attached to the request, 
    holding the current user's structural workforce footprint.
    """
    user: Optional[Any] = None
    party: Optional[Any] = None
    worker: Optional[Any] = None
    position: Optional[Any] = None
    supervisor: Optional[Any] = None
    org_unit: Optional[Any] = None
    is_active_worker: bool = False



class WorkforceContext:
    """
    User -> Workforce bridge.
    Serves as the high-level entry point for authenticated user workforce context.
    """

    @classmethod
    def _get_worker(cls, user) -> Any:
        """Centralized resolution of the worker entity with error handling."""
        party = getattr(user, "party", None)
        if not party:
            raise WorkerNotFound("User has no linked party.")
        
        worker = getattr(party, "workforce_member", None)
        if not worker:
            raise WorkerNotFound("Party is not linked to worker.")
        
        return worker

    @classmethod
    def get_user_party(cls, user):
        return getattr(user, "party", None)

    @classmethod
    def get_user_worker(cls, user):
        return cls._get_worker(user)

    @classmethod
    def get_user_contract(cls, user):
        return WorkforceResolver.get_active_contract(cls._get_worker(user))

    @classmethod
    def get_user_placement(cls, user):
        return WorkforceResolver.get_primary_placement(cls._get_worker(user))

    @classmethod
    def get_user_position(cls, user):
        return WorkforceResolver.get_primary_position(cls._get_worker(user))

    @classmethod
    def get_user_org_unit(cls, user):
        return WorkforceResolver.get_org_unit(cls._get_worker(user))

    @classmethod
    def get_user_deployments(cls, user):
        return WorkforceResolver.get_active_deployments(cls._get_worker(user))

    @classmethod
    def get_user_workstreams(cls, user):
        return WorkforceResolver.get_workstreams(cls._get_worker(user))

    @classmethod
    def get_user_roles(cls, user):
        return WorkforceResolver.get_roles(cls._get_worker(user))

    @classmethod
    def get_user_supervisor(cls, user, reporting_type=None):
        return WorkforceAuthority.resolve_supervisor(cls._get_worker(user), reporting_type)

    @classmethod
    def get_user_approval_actor(cls, user, level=1, reporting_type=None):
        return WorkforceAuthority.resolve_approval_actor(
            cls._get_worker(user), reporting_type=reporting_type, level=level
        )

    @classmethod
    def get_user_authority_holder(cls, user):
        return WorkforceAuthority.resolve_worker_authority(cls._get_worker(user))

    @classmethod
    def get_user_capacity(cls, user):
        return WorkforceResolver.get_capacity(cls._get_worker(user))

    @classmethod
    def get_user_remaining_capacity(cls, user):
        return WorkforceResolver.get_remaining_capacity(cls._get_worker(user))

    @classmethod
    def get_user_context(cls, user) -> WorkforceContextData:
        """Returns a comprehensive snapshot of the user's workforce footprint."""
        worker = cls._get_worker(user)
        party = cls.get_user_party(user)
        position = WorkforceResolver.get_primary_position(worker)
        supervisor = WorkforceAuthority.resolve_supervisor(worker)
        org_unit = WorkforceResolver.get_org_unit(worker)
        return WorkforceContextData(
            user=user,
            party=party,
            worker=worker,
            position=position,
            supervisor=supervisor,
            org_unit=org_unit,
            is_active_worker=True
            
        )
       