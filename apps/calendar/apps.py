from djangospice.app_registry import AppConfig


class CalendarConfig(AppConfig):
    default = True
    name = "apps.calendar"
    app_key = "app.calendar"

    
namespace = CalendarConfig.namespace