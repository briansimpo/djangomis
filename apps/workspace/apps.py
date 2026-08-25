from djangospice.apps import AppConfig

class WorkspaceConfig(AppConfig):
    name = "apps.workspace"
    label = "workspace"
    verbose_name = "Workspace"


namespace = WorkspaceConfig.namespace
