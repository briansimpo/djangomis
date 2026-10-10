from django.urls import path

from . import views


app_name = "calendar"


urlpatterns = [
    path(
        "",
        views.academic_context,
        name="academic-context",
    ),
]