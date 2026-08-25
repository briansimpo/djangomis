from django.db import models
from .queryset import OrgUnitQuerySet


class OrgUnitManager(models.Manager):

    def create(self, *args, **kwargs):
        raise RuntimeError(
            "Use OrgUnitService.create_unit() instead of direct create()."
        )

    def bulk_create(self, *args, **kwargs):
        raise RuntimeError(
            "bulk_create is disabled for OrgUnit. Use service layer."
        )
        
    def get_queryset(self):
        return OrgUnitQuerySet(
            self.model,
            using=self._db
        )

    def descendants_of(self, unit):
        return self.get_queryset().descendants_of(unit)

    def ancestors_of(self, unit):
        return self.get_queryset().ancestors_of(unit)
    
    def root_level(self):
        return self.filter(level=1)


