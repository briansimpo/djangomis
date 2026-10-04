from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from djangospice.db.models import BaseModel, OptionModel
from djangospice.enums.people import BloodType, Title, Gender, IDType, MaritalStatus
from apps.party.enums import PartyType


class OrganizationType(OptionModel):
    """
    Lookup matrix for classifying institutional layers (e.g., 'FACULTY', 'CAMPUS', 'DEPT').
    Inherits fields like code and name from OptionModel.
    """
    class Meta:
        verbose_name = _("Organization Type")
        verbose_name_plural = _("Organization Types")


class LegalStructure(BaseModel):
    """
    Reference table defining corporate/statutory legal entities (e.g., 'LLC', 'PLC', 'TRUST').
    """
    code = models.CharField(_("Code"), max_length=50, unique=True, help_text=_("Unique identifier token in CAPS."))
    name = models.CharField(_("Name"), max_length=100, help_text=_("Localized display name."))

    class Meta:
        verbose_name = _("Legal Structure")
        verbose_name_plural = _("Legal Structures")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Party(BaseModel):
    """
    The singular root identity node for all individuals, companies, and collections.
    """
    party_type = models.CharField(
        _("Party Type"), 
        max_length=100, 
        choices=PartyType.choices
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        
        related_name="party",
        verbose_name=_("User Account"),
        help_text=_("The authenticating user credential link authorizing active platform access.")
    )
    
    is_active = models.BooleanField(
        _("Is Active"), 
        default=True,
        help_text=_("Uncheck to globally suspend this party's system access and workflows.")
    )
    
    class Meta:
        verbose_name = _("Party")
        verbose_name_plural = _("Parties")
        ordering = ["-created"]

    def __str__(self):
        if hasattr(self, 'person_profile'):
            return f"{self.person_profile}"
        if hasattr(self, 'organization_profile'):
            return f"{self.organization_profile.name}"
        if hasattr(self, 'group_profile'):
            return f"{self.group_profile.name}"
        return f"{self.party_type}"
    

class Person(BaseModel):
    """
    Physical human representation of a Party profile.
    """
    party = models.OneToOneField(
        Party, 
        on_delete=models.CASCADE, 
        related_name='person_profile',
        verbose_name=_("Party Identity Link")
    )
    
    # Legal Identity
    title = models.CharField(_("Title"), max_length=100, choices=Title.choices, blank=True, null=True)
    first_name = models.CharField(_("First Name"), max_length=200)
    middle_name = models.CharField(_("Middle Name"), max_length=200, blank=True, null=True)
    last_name = models.CharField(_("Last Name"), max_length=200)
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)
    gender = models.CharField(_("Gender Identity"), max_length=100, choices=Gender.choices, blank=True, null=True)
    marital_status = models.CharField(_("Marital Status"), max_length=100, choices=MaritalStatus.choices, blank=True, null=True)
    
    # Government/Official Identification
    id_type = models.CharField(_("Identification Type"), max_length=100, choices=IDType.choices, blank=True, null=True)
    id_number = models.CharField(_("Identification Number"), max_length=100, blank=True, null=True)
    
    # Static Physical Biometrics
    blood_type = models.CharField(_("Blood Type"), max_length=50, choices=BloodType.choices, blank=True, null=True)
    height_cm = models.DecimalField(_("Height (cm)"), max_digits=5, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(_("Weight (kg)"), max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Organization(BaseModel):
    """
    Institutional, corporate, or operational representation of a Party profile.
    """
    party = models.OneToOneField(
        Party, 
        on_delete=models.CASCADE, 
        related_name='organization_profile',
        verbose_name=_("Party Identity Link")
    )
    name = models.CharField(_("Legal Name"), max_length=255)
    trade_name = models.CharField(
        _("Trade Name / DBA"), 
        max_length=255, 
        blank=True, 
        null=True, 
        help_text=_("Doing Business As (DBA) name if operating under alternative branding.")
    )
    org_type = models.ForeignKey(
        OrganizationType, 
        on_delete=models.PROTECT,
        related_name='organizations',
        verbose_name=_("Organization Type")
    )
    legal_structure = models.ForeignKey(
        LegalStructure, 
        on_delete=models.PROTECT, 
        related_name='organizations',
        blank=True, 
        null=True,
        verbose_name=_("Legal Structure")
    )
    registration_number = models.CharField(
        _("Commercial Registration Number"), 
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=_("Official business registry, company house, or charter number.")
    )
    tax_number = models.CharField(
        _("Tax ID / TPIN"), 
        max_length=50, 
        blank=True, 
        null=True, 
        help_text=_("TPIN, EIN, or national tax corporate registry handle.")
    )
    incorporation_date = models.DateField(
        _("Date of Incorporation"), 
        blank=True, 
        null=True, 
        help_text=_("The day the organization was legally formed or authorized.")
    )
    website = models.URLField(_("Official Website"), max_length=255, blank=True, null=True)
    fiscal_year_end_month = models.PositiveSmallIntegerField(
        _("Fiscal Year End Month"),
        blank=True, 
        null=True, 
        help_text=_("Month number (1-12) used to route budgeting, asset depreciation, and financial roll-ups.")
    )

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    
class Group(BaseModel):
    """
    Handles informal or structural group assemblies that do not present a structured corporate 
    charter, like temporary committees, clubs, work groups, or internal cohorts.
    """
    party = models.OneToOneField(
        Party, 
        on_delete=models.CASCADE, 
        related_name='group_profile',
        verbose_name=_("Party Identity Link")
    )
    name = models.CharField(_("Group Name"), max_length=255)
    group_type = models.CharField(
        _("Group Type"), 
        max_length=50,
        help_text=_("Classification of group clustering (e.g., COHORT, CLUB, COMMITTEE).")
    )
    description = models.TextField(_("Description / Purpose"), blank=True)

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.group_type})"
    
    
