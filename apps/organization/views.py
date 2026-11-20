from django.views.generic import FormView, TemplateView, UpdateView
from djangospice.http.shortcuts import navigate_to
from djangospice.utils import get_template_name, safe_reverse
from accounts.mixins import StaffLoginRequired
from apps.organization.forms import OrgUnitForm
from apps.organization.models.orgunits import OrgUnit
from apps.organization.apps import namespace


class HomeView(TemplateView):
    template_name = get_template_name("home", namespace)


class OrgUnitListView(StaffLoginRequired, TemplateView):
    template_name = get_template_name("list.html", namespace)


class OrgUnitStructureView(StaffLoginRequired, TemplateView):
    template_name = get_template_name("structure.html", namespace)
   

class OrgUnitCreateView(StaffLoginRequired, FormView):
    template_name = get_template_name("create.html", namespace)
    form_class =  OrgUnitForm

    def get_success_url(self):
        return safe_reverse("org_unit_list", namespace)

    def form_valid(self, form):
        form.save()
        url = self.get_success_url()
        return navigate_to(url).success("Record created successfully")


class OrgUnitUpdateView(StaffLoginRequired, UpdateView):
    template_name = get_template_name("edit.html", namespace)
    form_class = OrgUnitForm
    model = OrgUnit

    def get_success_url(self):
        return safe_reverse("org_unit_list", namespace)

    def form_valid(self, form):
        super().form_valid(form)
        url = self.get_success_url()
        return navigate_to(url).success("Record updated successfully")
        