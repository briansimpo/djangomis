class WorkforceError(Exception):
	pass


class PositionNotFound(WorkforceError):
    pass


class DuplicatePosition(WorkforceError):
    pass


class InvalidPositionState(WorkforceError):
    pass


class ReportingCycleDetected(WorkforceError):
    pass


class ReportingLineExists(WorkforceError):
    pass


class ReportingLineNotFound(WorkforceError):
    pass


class InvalidContractState(WorkforceError):
    pass
    
    
class ContractNotFound(WorkforceError):
    pass


class ActiveContractExists(WorkforceError):
    pass


class InvalidPlacementState(WorkforceError):
    pass


class PositionAlreadyOccupied(WorkforceError):
    pass


class PrimaryPlacementExists(WorkforceError):
    pass


class PlacementNotFound(WorkforceError):
    pass


class InvalidDeploymentState(WorkforceError):
    pass


class CapacityExceeded(WorkforceError):
    pass


class DeploymentNotFound(WorkforceError):
    pass


class SupervisionCycleDetected(WorkforceError):
    pass

class SupervisionNotFound(WorkforceError):
    pass


class InvalidSupervisionRelationship(WorkforceError):
    pass


class DelegationError(WorkforceError):
    pass


class InvalidDelegation(WorkforceError):
    pass


class DelegationNotFound(WorkforceError):
    pass



class WorkerNotFound(WorkforceError):
    pass


class PartyNotFound(WorkforceError):
    pass