from djangospice.app_registry import DjangospiceConfig

class WorkspaceConfig(DjangospiceConfig):
    name = "workspace"
    label = "workspace"
    verbose_name = "Workspace"


namespace = WorkspaceConfig.namespace
