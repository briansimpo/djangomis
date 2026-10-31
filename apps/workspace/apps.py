from djangospice.package import AppConfig

class WorkspaceConfig(AppConfig):
    name = "apps.workspace"
    verbose_name = "Workspace"


namespace = WorkspaceConfig.namespace
