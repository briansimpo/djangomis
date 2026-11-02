from djangospice.package import AppConfig

class WorkspaceConfig(AppConfig):
    name = "workspace"
    verbose_name = "Workspace"


namespace = WorkspaceConfig.namespace
