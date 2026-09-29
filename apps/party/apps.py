from djangospice_framework.apps import AppConfig

class PartyConfig(AppConfig):
    name = "apps.party"
    label = "party"
    verbose_name = "Party Master"


namespace = PartyConfig.namespace
