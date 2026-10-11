from djangospice.app_registry import AppConfig


class ChatConfig(AppConfig):
    name = "apps.chat"


namespace = ChatConfig.namespace