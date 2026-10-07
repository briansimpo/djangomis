from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from djangospice.db.models import BaseModel, OptionModel, FileFields
from djangospice.files.helpers import file_upload_path, get_file_path
from djangospice.urls import get_host_name
from djangospice.enums.contacts import ContactChannel, ContactUsage


class LogoMixin(FileFields):
    """
    An abstract mixin that provides standardized fields, storage paths,
    and property helpers for entities maintaining a logo and favicon.
    """
    LOGO_PATH = file_upload_path(get_file_path("logo"))
    FAVICON_PATH = file_upload_path(get_file_path("favicon"))

    logo = models.ImageField(
        _("Logo"), 
        upload_to=LOGO_PATH, 
        max_length=255, 
        blank=True, 
        null=True
    )
    favicon = models.ImageField(
        _("Favicon"), 
        upload_to=FAVICON_PATH, 
        max_length=255, 
        blank=True, 
        null=True
    )

    class Meta:
        abstract = True

    @property
    def logo_url(self) -> str:
        """Returns the relative media URL for the logo asset if present."""
        return self.logo.url if self.logo else ""
    
    @property
    def favicon_url(self) -> str:
        """Returns the relative media URL for the favicon asset if present."""
        return self.favicon.url if self.favicon else ""

    @property
    def logo_full_url(self) -> str:
        """Returns the absolute qualified URL for the logo asset."""
        if self.logo:
            return f"{get_host_name()}{self.logo_url}"
        return ""  
   
    @property
    def favicon_full_url(self) -> str:
        """Returns the absolute qualified URL for the favicon asset."""
        if self.favicon:
            return f"{get_host_name()}{self.favicon_url}"
        return ""
        

class Company(BaseModel, LogoMixin):
    """
    The root tenant / system owner configuration metadata model.
    Stores institutional, localization, financial calendar, and branding variables.
    """
    # Identity
    name = models.CharField(_("Name"), max_length=255)
    short_name = models.CharField(_("Short Name"), max_length=100, blank=True, null=True)
    legal_name = models.CharField(_("Legal Name"), max_length=255, blank=True, null=True)

    # Registration
    registration_number = models.CharField(_("Registration Number"), max_length=100, blank=True, null=True)
    tax_number = models.CharField(_("Tax Number"), max_length=100, blank=True, null=True)

    # Contact
    email = models.EmailField(_("Email Address"), blank=True, null=True)
    phone = models.CharField(_("Phone Number"), max_length=50, blank=True, null=True)
    website = models.URLField(_("Website"), blank=True, null=True)
    
    primary_url = models.URLField(_("Primary URL"), blank=True, null=True, help_text=_("Primary portal URL."))
    email_domain = models.CharField(_("Email Domain"), max_length=100, blank=True, null=True, help_text=_("Email domain for organization users."))
    support_email = models.EmailField(_("Support Email"), blank=True, null=True, help_text=_("Support or helpdesk email."))

    # Localization
    country = CountryField(_("Country"), blank=True, null=True)
    currency = models.CharField(_("Currency"), max_length=10, default="MWK")
    language = models.CharField(_("Language"), max_length=10, default="en")
    timezone = models.CharField(_("Timezone"), max_length=100, default="Africa/Blantyre")

    date_format = models.CharField(_("Date Format"), max_length=50, default="Y-m-d")
    number_format = models.CharField(_("Number Format"), max_length=50, default="1,234.56")

    # Calendar settings
    financial_year_start_month = models.PositiveSmallIntegerField(_("Financial Year Start Month"), default=1)
    financial_year_start_day = models.PositiveSmallIntegerField(_("Financial Year Start Day"), default=1)

    # Meta
    established_date = models.DateField(_("Established Date"), blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    metadata = models.JSONField(_("Metadata"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Company Profile")
        verbose_name_plural = _("company profile")
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    @property
    def primary_address(self):
        return self.addresses.filter(is_primary=True).first()
    
    @property
    def primary_phone(self):
        return self.contacts.filter(channel=ContactChannel.PHONE, is_primary=True).first()
    

class AddressType(OptionModel):
    """
    Lookup table configuration for classifying system addresses 
    (e.g., 'HEAD_OFFICE', 'BILLING', 'SHIPPING').
    """
    class Meta:
        verbose_name = _("Address Type")
        verbose_name_plural = _("address types")


class Address(BaseModel):
    """
    Physical geographic location mappings bound to a parent Company profile.
    Includes structured line configurations and spatial GIS attributes.
    """
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name="addresses",
        verbose_name=_("Company")
    )
    address_type = models.ForeignKey(
        AddressType, 
        on_delete=models.PROTECT,
        related_name="addresses",
        verbose_name=_("Address Type")
    )
    line1 = models.CharField(_("Address Line 1"), max_length=255)
    line2 = models.CharField(_("Address Line 2"), max_length=255, blank=True, null=True)
    city = models.CharField(_("City"), max_length=100)
    region = models.CharField(_("Region / State"), max_length=100, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100)
    postal_code = models.CharField(_("Postal / ZIP Code"), max_length=20, blank=True, null=True)
    
    # GIS coordinates
    latitude = models.DecimalField(_("Latitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_("Longitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_primary = models.BooleanField(_("Is Primary"), default=False)
    
    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("addresses")
        ordering = ["-is_primary", "created"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "address_type"], 
                name="uniq_company_address"
            )
        ]

    def __str__(self):
        return f"{self.line1}, {self.city}, {self.country}"
 

class Contact(BaseModel):
    """
    Multi-channel polymorphic communication mechanism (e.g., Work email, Emergency cellular)
    assigned explicitly to a singular Company profile instance.
    """
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name="contacts",
        verbose_name=_("Company")
    )
    channel = models.CharField(
        _("Contact Channel"),
        max_length=50, 
        choices=ContactChannel.choices,
        help_text=_("e.g., EMAIL, PHONE, WHATSAPP")
    )
    usage = models.CharField(
        _("Contact Usage"),
        max_length=50, 
        choices=ContactUsage.choices,
        help_text=_("e.g., WORK, PERSONAL, EMERGENCY")
    )
    value = models.CharField(
        _("Contact Value"),
        max_length=255,
        help_text=_("The actual email address, phone number, or social media handle string.")
    )
    is_primary = models.BooleanField(
        _("Is Primary"), 
        default=False,
        help_text=_("Designates if this is the primary communication method for this context.")
    )
    is_verified = models.BooleanField(
        _("Is Verified"), 
        default=False,
        help_text=_("Flagged true via verification systems.")
    )
    
    country_code = models.CharField(
        _("Country Code"),
        max_length=10, 
        blank=True, 
        null=True,
        help_text=_("International dialing prefix code.")
    )
    extension = models.CharField(
        _("Extension"),
        max_length=10, 
        blank=True, 
        null=True,
        help_text=_("Internal corporate office extension lines.")
    )
    
    notes = models.TextField(
        _("Internal Notes"),
        blank=True,
        help_text=_("Operational context.")
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("contacts")
        ordering = ["-is_primary", "channel", "-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "channel", "usage", "value"], 
                name="uniq_company_contact_profile"
            )
        ]

    def __str__(self):
        if self.country_code and self.channel == 'PHONE':
            return f"[{self.channel}] ({self.country_code}) {self.value}"
        return f"[{self.channel}] {self.value}"