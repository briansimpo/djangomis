from djangospice.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "apps.notifications"
    label = "notifications"
    
    
namespace = NotificationConfig.namespace