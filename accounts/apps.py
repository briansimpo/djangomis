from djangospice_framework.apps import AppConfig

class AccountsConfig(AppConfig):
    name = "accounts"
    namespace = "accounts"
    
    
namespace = AccountsConfig.namespace
