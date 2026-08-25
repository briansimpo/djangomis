from django.db import models
from .models import OrgUnit


class OrgUnitMixin(models.Model):
    org_unit = models.ForeignKey(OrgUnit, on_delete=models.PROTECT)

    class Meta:
        abstract = True
