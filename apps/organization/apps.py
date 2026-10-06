from djangospice.app_registry import AppConfig


class OrganizationConfig(AppConfig):
    name = "apps.organization"
    app_key = "apps.organization"
    app_url = "/organization"


namespace = OrganizationConfig.namespace