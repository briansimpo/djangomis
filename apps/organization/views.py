from django.shortcuts import render
from djangospice.utils import get_template_name
from apps.organization.apps import namespace


def home(request):
    template_name = get_template_name("home", namespace)
    return render(request, template_name)