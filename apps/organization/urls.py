from django.urls import path
from .apps import namespace
from . import views


app_name = namespace


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("org-unit/listview", views.OrgUnitListView.as_view(), name="org_unit_list"),
    path("org-unit/structure", views.OrgUnitStructureView.as_view(), name="org_unit_structure"),
    path("org-unit/create", views.OrgUnitCreateView.as_view(), name="create_org_unit"),
]
   