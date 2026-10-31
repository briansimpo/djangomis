from djangospice.package import AppConfig


class ChatConfig(AppConfig):
    name = "apps.chat"


namespace = ChatConfig.namespace