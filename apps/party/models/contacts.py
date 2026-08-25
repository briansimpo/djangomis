from django.db import models
from django.utils.translation import gettext_lazy as _
from djangospice.db.models import BaseModel, OptionModel
from enums.contacts import ContactChannel, ContactUsage
from .parties import Party


class AddressType(OptionModel):
    """
    Lookup table for classifying addresses (e.g., 'HOME', 'WORK', 'CAMPUS', 'BILLING').
    Inherits fields like code/name from OptionModel.
    """
    class Meta:
        verbose_name = _("Address Type")
        verbose_name_plural = _("Address Types")


class Address(BaseModel):
    """
    Physical geographic locations tied directly to a Party.
    """
    party = models.ForeignKey(
        Party, 
        on_delete=models.CASCADE, 
        related_name="party_addresses",
        verbose_name=_("Party")
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
    
    # GIS coordinates for automated maps and asset logistics routing
    latitude = models.DecimalField(_("Latitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_("Longitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_primary = models.BooleanField(_("Is Primary"), default=False)
    
    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ["-is_primary", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["party", "address_type"], 
                name="uniq_party_address"
            )
        ]

    def __str__(self):
        return f"{self.line1}, {self.city}, {self.country}"
 

class Contact(BaseModel):
    """
    Tracks telecommunication and digital communication access points for a Party.
    Accommodates global phone variations, verification lifecycles, and internal routing.
    """
    party = models.ForeignKey(
        Party, 
        on_delete=models.CASCADE, 
        related_name="party_contacts",
        verbose_name=_("Party")
    )
    channel = models.CharField(
        _("Contact Channel"),
        max_length=50, 
        choices=ContactChannel.choices,
        help_text=_("e.g., EMAIL, PHONE, WHATSAPP, SLACK")
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
        help_text=_("Designates if this is the primary communication method for this channel/usage context.")
    )
    is_verified = models.BooleanField(
        _("Is Verified"), 
        default=False,
        help_text=_("Flagged true via verification systems (OTP, email confirmation tokens).")
    )
    
    # Global/International Telephony Fields
    country_code = models.CharField(
        _("Country Code"),
        max_length=10, 
        blank=True, 
        null=True,
        help_text=_("International dialing prefix code (e.g., '+1', '+44', '+234').")
    )
    extension = models.CharField(
        _("Extension"),
        max_length=10, 
        blank=True, 
        null=True,
        help_text=_("Internal corporate office extension lines.")
    )
    
    # Internal Operational Audit Notes
    notes = models.TextField(
        _("Internal Notes"),
        blank=True,
        help_text=_("Operational context (e.g., 'Do not call after 5 PM', 'Shared office phone').")
    )

    class Meta:
        verbose_name = _("Contact Method")
        verbose_name_plural = _("Contact Methods")
        # Primaries float to the top of reverse lookups automatically
        ordering = ["-is_primary", "channel", "-created"]
        constraints = [
            # Safeguards database integrity against adding identical contact vectors 
            # under the exact same usage designation twice.
            models.UniqueConstraint(
                fields=["party", "channel", "usage", "value"], 
                name="uniq_party_contact_profile"
            )
        ]

    def __str__(self):
        if self.country_code and self.channel == 'PHONE':
            return f"[{self.channel}] ({self.country_code}) {self.value}"
        return f"[{self.channel}] {self.value}"