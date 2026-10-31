from djangospice.package import AppConfig


class PartyConfig(AppConfig):
    name = "apps.party"


namespace = PartyConfig.namespace
