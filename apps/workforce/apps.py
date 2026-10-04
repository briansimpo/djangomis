from djangospice.app_registry import AppConfig


class WorkforceConfig(AppConfig):
    name = "apps.workforce"
  

namespace = WorkforceConfig.namespace