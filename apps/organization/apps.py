from django.db.models.signals import post_migrate
from djangospice_framework.apps import AppConfig
from djangospice_installer.installer import AppInstaller


class OrganizationConfig(AppConfig):
    name = "apps.organization"
    label = "organization"
    verbose_name = "Organization"
    description = ""
    url = "organization/"
    icon = "icon.png"

    def ready(self) -> None:
        post_migrate.connect(self.install, sender=self)

    def install(self, **kwargs):
        installer = AppInstaller(self)
        installer.install()

namespace = OrganizationConfig.namespace