from django.urls import path
from .apps import namespace
from . import views

app_name = namespace


urlpatterns = [
    path("", views.HomeView.as_view() , name="home"),
]
