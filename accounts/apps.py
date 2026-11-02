from djangospice.package import AppConfig

class AccountsConfig(AppConfig):
    name = "accounts"
    verbose_name = "My Account"
    
namespace = AccountsConfig.namespace
