from djangospice.app_registry import AppConfig


class PartyConfig(AppConfig):
    name = "apps.party"


namespace = PartyConfig.namespace
