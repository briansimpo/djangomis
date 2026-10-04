from djangospice.app_registry import AppConfig


class UsersConfig(AppConfig):
    name = "users"
    verbose_name = "Users"
    app_key = "users"


namespace = UsersConfig.namespace
