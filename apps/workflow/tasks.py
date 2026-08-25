import pydoc
import logging
from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_async_workflow_handler(self, handler_path: str, instance_id: any, actor_id: any, extra_context: dict = None):
    """
    Background worker task to execute workflow scripts asynchronously.
    """
    # Import inside the function to prevent circular dependency issues on load
    from .models import WorkflowInstance 
    
    try:
        # Reconstruct the ORM context from the serialized IDs
        instance = WorkflowInstance.objects.get(id=instance_id)
        actor = User.objects.filter(id=actor_id).first() if actor_id else None
        
        context = {
            "instance": instance,
            "actor": actor,
            **(extra_context or {})
        }

        # Load and execute the handler
        handler_class = pydoc.locate(handler_path)
        if not handler_class:
            logger.error(f"Failed to locate async workflow handler: {handler_path}")
            return

        handler_instance = handler_class()
        handler_instance.execute(context)
        
    except Exception as e:
        logger.exception(f"Async handler execution failed for {handler_path}: {str(e)}")
        # If the external API fails, retry up to 3 times, 1 minute apart
        raise self.retry(exc=e)