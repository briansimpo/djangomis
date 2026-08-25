from apps.workflow.models import Workflow

def get_workflows(request=None):
    return Workflow.objects.filter(is_active=True)

