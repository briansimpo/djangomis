from djangospice.app_registry import AppConfig


class OrganizationConfig(AppConfig):
    name = "apps.organization"
    app_key = "apps.organization"
    app_name = "Org Structure"


namespace = OrganizationConfig.namespace