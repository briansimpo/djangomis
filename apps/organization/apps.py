from djangospice.app_registry import AppConfig


class OrganizationConfig(AppConfig):
    name = "apps.organization"
    app_key = "apps.organization"


namespace = OrganizationConfig.namespace