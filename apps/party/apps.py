from djangospice.app_registry import DjangospiceConfig


class PartyConfig(DjangospiceConfig):
    name = "apps.party"


namespace = PartyConfig.namespace
