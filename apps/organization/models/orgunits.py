from django.db import models
from djangospice.db.models import BaseModel, OptionModel
from djangospice.core.formatting import normalize
from apps.organization.managers import OrgUnitManager


class OrgUnitType(OptionModel):
    level = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = "Org Unit Type"
        verbose_name_plural = "org unit types"


class OrgUnit(BaseModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    type = models.ForeignKey(OrgUnitType, on_delete=models.PROTECT)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", blank=True, null=True)
    level = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)
    
    objects = OrgUnitManager()

    class Meta:
        verbose_name = "Org Unit"
        verbose_name_plural = "org units"
        constraints = [
            models.UniqueConstraint(
                fields=["code", "type", "level"],
                name="uniq_org_unit_code"
            )
        ]

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.name = normalize(self.name)

        if self.parent:
            self.level = self.parent.level + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class OrgUnitClosure(BaseModel):
    ancestor = models.ForeignKey(OrgUnit, related_name="ancestor_links", on_delete=models.CASCADE)
    descendant = models.ForeignKey(OrgUnit, related_name="descendant_links", on_delete=models.CASCADE)
    depth = models.IntegerField()

    class Meta:
        unique_together = ("ancestor", "descendant")
        indexes = [
            models.Index(fields=["ancestor"]),
            models.Index(fields=["descendant"]),
            models.Index(fields=["ancestor", "descendant"]),
        ]

