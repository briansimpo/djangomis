from djangospice_framework.apps import AppConfig

class WorkspaceConfig(AppConfig):
    name = "workspace"
    label = "workspace"
    verbose_name = "Workspace"


namespace = WorkspaceConfig.namespace
