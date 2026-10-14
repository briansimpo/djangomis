from django.urls import path
from .apps import namespace
from . import views

app_name = namespace


urlpatterns = [
    path("", views.HomeView.as_view() , name="home"),
    path("get-apps", views.GetAppsView.as_view() , name="get_apps"),
]
