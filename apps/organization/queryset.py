from django.db import models


class OrgUnitQuerySet(models.QuerySet):

    def descendants_of(self, unit):
        return self.filter(
            ancestor_links__ancestor=unit
        ).distinct()

    def ancestors_of(self, unit):
        return self.filter(
            descendant_links__descendant=unit
        ).distinct()
