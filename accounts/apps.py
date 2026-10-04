from djangospice.app_registry import AppConfig

class AccountsConfig(AppConfig):
    name = "accounts"
    namespace = "accounts"
    
    
namespace = AccountsConfig.namespace
