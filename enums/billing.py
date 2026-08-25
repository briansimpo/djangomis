from django.db import models
from django.utils.translation import gettext_lazy as _


class BillingRate(models.TextChoices):
    FLAT = "flat", _("Flat")
    PER_USER = "per_user", _("Per User")
    PER_MODULE = "per_module", _("Per Module")


class BillingType(models.TextChoices):
    PREPAID = "prepaid", _("Prepaid")
    POSTPAID = "postpaid", _("Postpaid")


class BillingCycle(models.TextChoices):
    ONE_TIME = "one_time", _("One Time")
    MONTHLY = "monthly", _("Per Month")
    QUARTERLY = "quarterly", _("Per Quarter")
    TRIMESTERLY = "trimesterly", _("Per Trimester")
    SEMESTERLY = "semesterly", _("Per Semester")
    YEARLY = "yearly", _("Per Year")