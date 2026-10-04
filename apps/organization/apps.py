from djangospice.app_registry import DjangospiceConfig


class OrganizationConfig(DjangospiceConfig):
    name = "apps.organization"
    

namespace = OrganizationConfig.namespace