from django.urls import path
from .apps import namespace
from . import views

app_name = namespace


urlpatterns = [
    path("", views.IndexView.as_view() , name="index"),
    path("workspace", views.HomeView.as_view() , name="workspace"),
    path("switch-unit", views.SwitchOrgUnitView.as_view(), name="switch_org_unit"),
    path("switch-period", views.SwitchPeriodView.as_view(), name="switch_period"),
    path("get-apps", views.GetAppsView.as_view() , name="get_apps"),
]
