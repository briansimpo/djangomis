from django.db.models.signals import post_migrate
from django.utils.module_loading import autodiscover_modules
from djangospice.package import AppConfig


class WorkflowConfig(AppConfig):
    name = "apps.workflow"

    def ready(self):
        post_migrate.connect(self.register, sender=self)

        
    def register(self, **kwargs):
        from apps.workflow.integration.loader import load_workflows
        try:
            autodiscover_modules("workflows")
            load_workflows()
        except Exception as e:
            pass


namespace = WorkflowConfig.namespace