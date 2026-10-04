import logging
from django.db import transaction
from apps.workflow.models import Workflow, WorkflowState
from apps.workflow.integration.registry import registry

logger = logging.getLogger(__name__)


def load_workflows():

    try:
        workflows =  []
        with transaction.atomic():
            for approval_workflow in registry.get_all():

                workflow, _ = Workflow.objects.update_or_create( 
                    code=approval_workflow.code, 
                    defaults={
                        "name": approval_workflow.name,
                        "description": approval_workflow.description
                    },
                )

                states = approval_workflow.states
                
                for state in states:

                    instance, _ = WorkflowState.objects.update_or_create(
                        workflow=workflow,
                        code=state.code,
                        order=state.order,
                        defaults={ 
                            "name": state.name,
                            "is_terminal": state.is_terminal,
                        },
                    )
                workflows.append(workflow)

        if len(workflows) > 0:         
            logger.info("Workflows synchronized successfully.")

    except Exception as e:
        logger.error(str(e))
    
