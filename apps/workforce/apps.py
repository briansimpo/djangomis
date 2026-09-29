from django.db.models.signals import post_migrate
from djangospice_framework.apps import AppConfig
from djangospice_installer.installer import AppInstaller


class WorkforceConfig(AppConfig):
    name = "apps.workforce"
    label = "workforce"
    verbose_name = "Workforce"
    description = ""
    url = "workforce/"
    icon = "icon.png"
    is_default = True

    def ready(self):
        post_migrate.connect(self.install, sender=self)
        post_migrate.connect(self.register, sender=self)

    def install(self, **kwargs):
        installer = AppInstaller(self)
        installer.install()
        


namespace = WorkforceConfig.namespace