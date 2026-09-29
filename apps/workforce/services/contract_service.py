from datetime import date
from typing import Optional, Dict, Any, List, Iterable
from django.db import transaction
from django.db.models import Q, QuerySet, Count
from django.utils import timezone
from apps.workforce.models import Contract, Worker
from apps.workforce.enums import ContractStatus
from apps.workforce.exceptions import InvalidContractState, ContractNotFound


class ContractValidationService:
    """Handles pure logical checks, state evaluations, and boundary validations."""

    @classmethod
    def validate_contract_dates(cls, valid_from: date, valid_until: Optional[date]) -> bool:
        if valid_until and valid_until < valid_from:
            raise InvalidContractState("Contract end date cannot be before start date.")
        return True

    @classmethod
    def is_active(cls, contract: Contract) -> bool:
        today = timezone.now().date()
        return (
            contract.status == ContractStatus.ACTIVE
            and contract.valid_from <= today
            and (contract.valid_until is None or contract.valid_until >= today)
        )

    @classmethod
    def validate_contract(cls, contract: Contract) -> bool:
        if not cls.is_active(contract):
            raise InvalidContractState("Contract is not active.")
        return True
  

class ContractQueryService:
    """Handles direct base-level queries, search filters, and record retrievals."""

    @classmethod
    def get_active_contracts(cls, worker: Worker) -> QuerySet[Contract]:
        today = timezone.now().date()
        return (
            Contract.objects.select_related("worker", "contract_type", "sponsor_party")
            .filter(worker=worker, status=ContractStatus.ACTIVE, valid_from__lte=today)
            .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
            .order_by("-valid_from")
        )

    @classmethod
    def get_contract(cls, contract_id: Any) -> Contract:
        try:
            return Contract.objects.select_related(
                "worker", "contract_type", "sponsor_party"
            ).get(pk=contract_id)
        except Contract.DoesNotExist:
            raise ContractNotFound(f"Contract {contract_id} not found.")

    @classmethod
    def get_worker_contract(cls, worker: Worker) -> Optional[Contract]:
        return cls.get_active_contracts(worker).first()

    @classmethod
    def has_active_contract(cls, worker: Worker) -> bool:
        return cls.get_active_contracts(worker).exists()

    @classmethod
    def get_worker_contracts(cls, worker: Worker) -> QuerySet[Contract]:
        return (
            Contract.objects.select_related("contract_type", "sponsor_party")
            .filter(worker=worker)
            .order_by("-valid_from")
        )

    @classmethod
    def get_expiring_contracts(cls, before_date: date) -> QuerySet[Contract]:
        return Contract.objects.filter(
            status=ContractStatus.ACTIVE,
            valid_until__isnull=False,
            valid_until__lte=before_date,
        ).select_related("worker", "contract_type")

    @classmethod
    def search_contracts(
        cls,
        worker: Optional[Worker] = None,
        contract_type: Optional[Any] = None,
        sponsor_party: Optional[Any] = None,
        status: Optional[str] = None,
        query: Optional[str] = None,
    ) -> QuerySet[Contract]:
        qs = Contract.objects.select_related("worker", "worker__party", "contract_type", "sponsor_party")

        if worker:
            qs = qs.filter(worker=worker)
        if contract_type:
            qs = qs.filter(contract_type=contract_type)
        if sponsor_party:
            qs = qs.filter(sponsor_party=sponsor_party)
        if status:
            qs = qs.filter(status=status)
        if query:
            qs = qs.filter(
                Q(worker__worker_number__icontains=query) | Q(worker__party__name__icontains=query)
            )
        return qs.order_by("-valid_from")
    

class ContractMutationService:
    """Executes state changes, lifecycle modifications, and bulk updates securely."""

    @classmethod
    @transaction.atomic
    def create_contract(
        cls, worker: Worker, contract_type: Any, sponsor_party: Any, valid_from: date,
        valid_until: Optional[date] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Contract:
        ContractValidationService.validate_contract_dates(valid_from, valid_until)
        return Contract.objects.create(
            worker=worker, sponsor_party=sponsor_party, contract_type=contract_type,
            valid_from=valid_from, valid_until=valid_until, metadata=metadata or {},
            status=ContractStatus.ACTIVE,
        )

    @classmethod
    @transaction.atomic
    def activate_contract(cls, contract: Contract) -> Contract:
        if contract.status == ContractStatus.ACTIVE:
            return contract
        if contract.status == ContractStatus.TERMINATED:
            raise InvalidContractState("Cannot reactivate terminated contract.")
        contract.status = ContractStatus.ACTIVE
        contract.save(update_fields=["status", "modified"])
        return contract

    @classmethod
    @transaction.atomic
    def suspend_contract(cls, contract: Contract) -> Contract:
        if contract.status == ContractStatus.TERMINATED:
            raise InvalidContractState("Cannot suspend terminated contract.")
        contract.status = ContractStatus.SUSPENDED
        contract.save(update_fields=["status", "modified"])
        return contract

    @classmethod
    @transaction.atomic
    def terminate_contract(cls, contract: Contract, termination_date: date) -> Contract:
        if termination_date < contract.valid_from:
            raise InvalidContractState("Termination date cannot precede contract start.")
        contract.status = ContractStatus.TERMINATED
        contract.valid_until = termination_date
        contract.save(update_fields=["status", "valid_until", "modified"])
        return contract

    @classmethod
    @transaction.atomic
    def renew_contract(cls, contract: Contract, new_end_date: date) -> Contract:
        if contract.valid_until and new_end_date <= contract.valid_until:
            raise InvalidContractState("Renewal must extend validity.")
        contract.valid_until = new_end_date
        if contract.status == ContractStatus.SUSPENDED:
            contract.status = ContractStatus.ACTIVE
        contract.save()
        return contract

    @classmethod
    @transaction.atomic
    def archive_contract(cls, contract: Contract) -> Contract:
        contract.metadata = {**(contract.metadata or {}), "archived": True}
        contract.save(update_fields=["metadata", "modified"])
        return contract

    @classmethod
    @transaction.atomic
    def clone_contract(
        cls, contract: Contract, valid_from: date, valid_until: Optional[date] = None, status: str = ContractStatus.ACTIVE
    ) -> Contract:
        return Contract.objects.create(
            worker=contract.worker, sponsor_party=contract.sponsor_party, contract_type=contract.contract_type,
            valid_from=valid_from, valid_until=valid_until, status=status, metadata=dict(contract.metadata or {}),
        )

    @classmethod
    @transaction.atomic
    def change_sponsor(cls, contract: Contract, sponsor_party: Any) -> Contract:
        contract.sponsor_party = sponsor_party
        contract.save(update_fields=["sponsor_party", "modified"])
        return contract

    @classmethod
    @transaction.atomic
    def change_contract_type(cls, contract: Contract, contract_type: Any) -> Contract:
        contract.contract_type = contract_type
        contract.save(update_fields=["contract_type", "modified"])
        return contract

    @classmethod
    @transaction.atomic
    def bulk_activate(cls, contracts: Iterable[Contract]) -> List[Contract]:
        contract_ids = [c.id for c in contracts]
        Contract.objects.filter(id__in=contract_ids).update(status=ContractStatus.ACTIVE)
        return list(Contract.objects.filter(id__in=contract_ids))

    @classmethod
    @transaction.atomic
    def bulk_suspend(cls, contracts: Iterable[Contract]) -> List[Contract]:
        contract_ids = [c.id for c in contracts]
        Contract.objects.filter(id__in=contract_ids).update(status=ContractStatus.SUSPENDED)
        return list(Contract.objects.filter(id__in=contract_ids))

    @classmethod
    @transaction.atomic
    def bulk_terminate(cls, contracts: Iterable[Contract], termination_date: date) -> List[Contract]:
        contract_ids = [c.id for c in contracts]
        Contract.objects.filter(id__in=contract_ids).update(status=ContractStatus.TERMINATED, valid_until=termination_date)
        return list(Contract.objects.filter(id__in=contract_ids))
    
    
class ContractAnalyticsService:
    """Summarizes macro metrics and serializes timeline records for external views."""

    @classmethod
    def get_contract_timeline(cls, worker: Worker) -> List[Dict[str, Any]]:
        return [
            {
                "id": contract.id,
                "type": str(contract.contract_type) if contract.contract_type else None,
                "status": contract.status,
                "from": contract.valid_from,
                "to": contract.valid_until,
            }
            for contract in ContractQueryService.get_worker_contracts(worker)
        ]

    @classmethod
    def get_contract_statistics(cls) -> Dict[str, int]:
        counts = Contract.objects.aggregate(
            active=Count("id", filter=Q(status=ContractStatus.ACTIVE)),
            suspended=Count("id", filter=Q(status=ContractStatus.SUSPENDED)),
            terminated=Count("id", filter=Q(status=ContractStatus.TERMINATED))
        )
        return {
            "active": counts["active"] or 0,
            "suspended": counts["suspended"] or 0,
            "terminated": counts["terminated"] or 0,
        }
        

class ContractService:
    """
    Public API Service Facade for Employment Contracts.
    
    Preserves historical method names and signatures perfectly to secure 
    backwards-compatibility across the codebase while delegating complex 
    logic to granular, internal domain modules.
    """

    @classmethod
    def validate_contract_dates(cls, valid_from: date, valid_until: Optional[date]) -> bool:
        return ContractValidationService.validate_contract_dates(valid_from, valid_until)

    @classmethod
    def is_active(cls, contract: Contract) -> bool:
        return ContractValidationService.is_active(contract)

    @classmethod
    def validate_contract(cls, contract: Contract) -> bool:
        return ContractValidationService.validate_contract(contract)

    @classmethod
    def get_active_contracts(cls, worker: Worker) -> QuerySet[Contract]:
        return ContractQueryService.get_active_contracts(worker)

    @classmethod
    def get_contract(cls, contract_id: Any) -> Contract:
        return ContractQueryService.get_contract(contract_id)

    @classmethod
    def get_worker_contract(cls, worker: Worker) -> Optional[Contract]:
        return ContractQueryService.get_worker_contract(worker)

    @classmethod
    def has_active_contract(cls, worker: Worker) -> bool:
        return ContractQueryService.has_active_contract(worker)

    @classmethod
    def get_worker_contracts(cls, worker: Worker) -> QuerySet[Contract]:
        return ContractQueryService.get_worker_contracts(worker)

    @classmethod
    def get_contract_history(cls, worker: Worker) -> QuerySet[Contract]:
        # Alias matching historical naming convention
        return ContractQueryService.get_worker_contracts(worker)

    @classmethod
    def get_expiring_contracts(cls, before_date: date) -> QuerySet[Contract]:
        return ContractQueryService.get_expiring_contracts(before_date)

    @classmethod
    def search_contracts(
        cls,
        worker: Optional[Worker] = None,
        contract_type: Optional[Any] = None,
        sponsor_party: Optional[Any] = None,
        status: Optional[str] = None,
        query: Optional[str] = None,
    ) -> QuerySet[Contract]:
        return ContractQueryService.search_contracts(worker, contract_type, sponsor_party, status, query)

    @classmethod
    def create_contract(
        cls, worker: Worker, contract_type: Any, sponsor_party: Any, valid_from: date,
        valid_until: Optional[date] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Contract:
        return ContractMutationService.create_contract(worker, contract_type, sponsor_party, valid_from, valid_until, metadata)

    @classmethod
    def activate_contract(cls, contract: Contract) -> Contract:
        return ContractMutationService.activate_contract(contract)

    @classmethod
    def suspend_contract(cls, contract: Contract) -> Contract:
        return ContractMutationService.suspend_contract(contract)

    @classmethod
    def terminate_contract(cls, contract: Contract, termination_date: date) -> Contract:
        return ContractMutationService.terminate_contract(contract, termination_date)

    @classmethod
    def renew_contract(cls, contract: Contract, new_end_date: date) -> Contract:
        return ContractMutationService.renew_contract(contract, new_end_date)

    @classmethod
    def archive_contract(cls, contract: Contract) -> Contract:
        return ContractMutationService.archive_contract(contract)

    @classmethod
    def clone_contract(
        cls, contract: Contract, valid_from: date, valid_until: Optional[date] = None, status: str = "ACTIVE"
    ) -> Contract:
        return ContractMutationService.clone_contract(contract, valid_from, valid_until, status)

    @classmethod
    def change_sponsor(cls, contract: Contract, sponsor_party: Any) -> Contract:
        return ContractMutationService.change_sponsor(contract, sponsor_party)

    @classmethod
    def change_contract_type(cls, contract: Contract, contract_type: Any) -> Contract:
        return ContractMutationService.change_contract_type(contract, contract_type)

    @classmethod
    def bulk_activate(cls, contracts: Iterable[Contract]) -> List[Contract]:
        return ContractMutationService.bulk_activate(contracts)

    @classmethod
    def bulk_suspend(cls, contracts: Iterable[Contract]) -> List[Contract]:
        return ContractMutationService.bulk_suspend(contracts)

    @classmethod
    def bulk_terminate(cls, contracts: Iterable[Contract], termination_date: date) -> List[Contract]:
        return ContractMutationService.bulk_terminate(contracts, termination_date)

    # --- Analytics & Reporting API ---

    @classmethod
    def get_contract_timeline(cls, worker: Worker) -> List[Dict[str, Any]]:
        return ContractAnalyticsService.get_contract_timeline(worker)

    @classmethod
    def get_contract_statistics(cls) -> Dict[str, int]:
        return ContractAnalyticsService.get_contract_statistics()