from django.views.generic import TemplateView
from djangospice.utils import get_template_name
from accounts.mixins import StaffLoginRequired
from .apps import namespace


class HomeView(StaffLoginRequired, TemplateView):
    template_name = get_template_name("home.html", namespace)
    