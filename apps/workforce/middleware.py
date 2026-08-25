from django.utils.functional import SimpleLazyObject
from apps.workforce.resolvers.workforce_context import WorkforceContext, WorkforceContextData
from apps.workforce.exceptions import WorkerNotFound


def build_lazy_workforce_context(request) -> WorkforceContextData:
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


class WorkforceContextMiddleware:
    """
    Middleware to attach the active user's structural workforce 
    context to the request cycle lazily.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach the context as a SimpleLazyObject. 
        # The database is NOT hit until `request.workforce.worker` (etc.) is evaluated.
        request.workforce = SimpleLazyObject(lambda: build_lazy_workforce_context(request))
        
        response = self.get_response(request)
        return response