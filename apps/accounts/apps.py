from djangospice.apps import AppConfig

class AccountsConfig(AppConfig):
    name = "apps.accounts"
    namespace = "accounts"
    
    
namespace = AccountsConfig.namespace
