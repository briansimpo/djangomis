from djangospice.package import AppConfig

class AccountsConfig(AppConfig):
    name = "accounts"
    
namespace = AccountsConfig.namespace
