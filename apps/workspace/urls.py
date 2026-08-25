from django.urls import path
from .apps import namespace
from . import views

app_name = namespace


urlpatterns = [
    path("", views.HomeView.as_view() , name="home"),
    path("switch/unit", views.SwitchOrgUnitView.as_view(), name="switch_org_unit"),
    path("switch/period", views.SwitchPeriodView.as_view(), name="switch_period"),
    path("myapps", views.UserAppsView.as_view() , name="user_apps"),
]
