from django.contrib import messages
from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from djangospice.utils import get_template_name, safe_redirect
from accounts.mixins import StaffLoginRequired
from apps.organization.apps import namespace
from apps.organization.forms import OrgUnitForm


class HomeView(TemplateView):
    template_name = get_template_name("home", namespace)



class CreateOrgUnitiew(StaffLoginRequired, FormView):
    template_name = get_template_name("create.html", namespace)
    form_class =  OrgUnitForm


    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Record created successfully")
        return safe_redirect("home", namespace)