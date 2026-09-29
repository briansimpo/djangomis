from django.db import models

from apps.party.models.parties import Party
  
class PartyMixin(models.Model):
    party  = models.ForeignKey(Party, on_delete=models.CASCADE)

    class Meta:
        abstract = True