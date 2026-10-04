from djangospice.app_registry import DjangospiceConfig

class AccountsConfig(DjangospiceConfig):
    name = "accounts"
    namespace = "accounts"
    
    
namespace = AccountsConfig.namespace
