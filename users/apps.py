from djangospice.app_registry import AppConfig


class UsersConfig(AppConfig):
    name = "users"
    app_key = "users"
    app_url = "/users"


namespace = UsersConfig.namespace
