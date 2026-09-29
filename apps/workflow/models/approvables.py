from abc import ABC, abstractmethod
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from djangospice_framework.db.models import BaseModel
from apps.workflow.enums import WorkflowStatus
from apps.organization.models import OrgUnit


User = get_user_model()
   

class BaseApprovableModel(BaseModel):
    status = models.CharField(max_length=20, choices=WorkflowStatus.choices, default=WorkflowStatus.DRAFT)
    submitted_by = models.ForeignKey(User,blank=True, null=True, on_delete=models.SET_NULL, related_name="submitted_%(class)s")
    submitted_at = models.DateTimeField(blank=True, null=True)
    org_unit = models.ForeignKey(OrgUnit, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
        

    def is_draft(self):
        return self.status == WorkflowStatus.DRAFT

    def is_submitted(self):
        return self.status == WorkflowStatus.SUBMITTED

    def is_approved(self):
        return self.status == WorkflowStatus.APPROVED

    def is_rejected(self):
        return self.status == WorkflowStatus.REJECTED

    def submit(self, submitted_by=None):
        self.status = WorkflowStatus.SUBMITTED
        self.submitted_at = timezone.now()
        self.submitted_by = submitted_by
        self.save(update_fields=["status", "submitted_at", "submitted_by"])

    def set_org_unit(self, org_unit):
        self.org_unit = org_unit
        self.save(update_fields=["org_unit"])
        
    def set_calendar_period(self, calendar_period):
        self.calendar_period = calendar_period
        self.save(update_fields=["calendar_period"])
    

class ApprovableModelMixin:

    @abstractmethod
    def get_summary(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_details(self) -> dict:
        raise NotImplementedError

    def get_attachments(self):
        return []

    def on_approved(self, context=None):
        pass

    def on_rejected(self, context=None):
        pass

    def on_transition(self, from_state, to_state, context=None):
        pass
    
    
class ApprovableModel(BaseApprovableModel, ApprovableModelMixin):
    
    class Meta:
        abstract = True