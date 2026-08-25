from django.db.models.signals import post_migrate
from djangospice.apps import AppConfig
from djangospice.apps.installer import AppInstaller


class UsersConfig(AppConfig):
    name = "djangospice.users"
    namespace = "users"
    verbose_name = "Users"

    def ready(self) -> None:
        post_migrate.connect(self.install, sender=self)
        
    def install(self, **kwargs):
        installer = AppInstaller(self)
        installer.install()

namespace = UsersConfig.namespace
