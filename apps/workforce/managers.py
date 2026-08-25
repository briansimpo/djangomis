from django.db import models
from .querysets import WorkforceScopeQuerySet


class WorkforceScopeManager(models.Manager):
    
    def get_queryset(self):
        return WorkforceScopeQuerySet(self.model, using=self._db)

    def authorized(self, request):
        return self.get_queryset().authorized(request) 