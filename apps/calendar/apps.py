from djangospice.app_registry import DjangospiceConfig


class CalendarConfig(DjangospiceConfig):
    name = "apps.calendar"
    
namespace = CalendarConfig.namespace