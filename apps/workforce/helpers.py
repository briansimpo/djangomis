from apps.workforce.resolvers.workforce_context import WorkforceContext, WorkforceContextData
from apps.workforce.exceptions import WorkerNotFound
from apps.workforce.resolvers.workforce_context import WorkforceContext

def get_user_org_unit(user):
    user_org_unit = WorkforceContext.get_user_org_unit(user)
    return user_org_unit


def get_workforce_context(request) -> WorkforceContextData:
    """
    Evaluates and builds the context. 
    This function is ONLY triggered the first time `request.workforce` is accessed.
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return WorkforceContext()

    try:
        return WorkforceContext.get_user_context(request.user)
    except WorkerNotFound:
        return WorkforceContext()