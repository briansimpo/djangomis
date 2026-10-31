from djangospice.package import AppConfig


class CalendarConfig(AppConfig):
    name = "apps.calendar"
    app_key = "app.calendar"
    app_name = "Org Calendar"


    
namespace = CalendarConfig.namespace