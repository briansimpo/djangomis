from django.db.models.signals import post_migrate
from django.utils.module_loading import autodiscover_modules
from djangospice_framework.apps import AppConfig
from djangospice_installer.installer import AppInstaller


class WorkflowConfig(AppConfig):
    name = "apps.workflow"
    label = "workflow"
    verbose_name = "Workflow"
    description = ""
    url = "workflow/"
    icon = "icon.png"
    is_default = True

    def ready(self):
        post_migrate.connect(self.install, sender=self)
        post_migrate.connect(self.register, sender=self)

    def install(self, **kwargs):
        installer = AppInstaller(self)
        installer.install()
        
    def register(self, **kwargs):
        from apps.workflow.integration.loader import load_workflows
        try:
            autodiscover_modules("workflows")
            load_workflows()
        except Exception as e:
            pass


namespace = WorkflowConfig.namespace