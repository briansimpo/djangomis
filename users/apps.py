from djangospice.app_registry import DjangospiceConfig


class UsersConfig(DjangospiceConfig):
    name = "users"
    verbose_name = "Users"


namespace = UsersConfig.namespace
