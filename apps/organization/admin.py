from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Company, AddressType, Address, Contact


class AddressInline(admin.TabularInline):
    """Inline administration for Address records within the Company change form."""
    model = Address
    extra = 1
    fields = ["address_type", "line1", "city", "country", "is_primary"]
    classes = ["collapse"]


class ContactInline(admin.TabularInline):
    """Inline administration for Contact records within the Company change form."""
    model = Contact
    extra = 1
    fields = ["channel", "usage", "value", "is_primary", "is_verified"]
    classes = ["collapse"]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin configuration for the Company core profile metadata."""
    list_display = ["name", "short_name", "email", "phone", "country", "is_active"]
    list_filter = ["is_active", "country", "currency", "language"]
    search_fields = ["name", "short_name", "legal_name", "email", "registration_number"]
    inlines = [AddressInline, ContactInline]
    
    fieldsets = (
        (_("Identity"), {
            "fields": ("name", "short_name", "legal_name")
        }),
        (_("Branding Assets"), {
            "fields": ("logo", "favicon"),
            "description": _("Upload corporate identity visuals.")
        }),
        (_("Regulatory Registration"), {
            "fields": ("registration_number", "tax_number")
        }),
        (_("Primary Contact channels"), {
            "fields": ("email", "phone", "website", "primary_url", "email_domain", "support_email")
        }),
        (_("Localization Defaults"), {
            "fields": ("country", "currency", "language", "timezone", "date_format", "number_format")
        }),
        (_("Operational Parameters"), {
            "fields": ("financial_year_start_month", "financial_year_start_day", "established_date", "is_active")
        }),
        (_("Advanced Extensibility"), {
            "fields": ("description", "metadata"),
            "classes": ("collapse",)
        }),
    )


@admin.register(AddressType)
class AddressTypeAdmin(admin.ModelAdmin):
    """Admin representation for Address classification types."""
    list_display = ["name", "code", "is_active"]
    search_fields = ["name", "code"]
    list_filter = ["is_active"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Standalone administration for geographic and physical corporate locations."""
    list_display = ["company", "address_type", "line1", "city", "country", "is_primary"]
    list_filter = ["address_type", "is_primary", "country"]
    search_fields = ["company__name", "line1", "city", "postal_code"]
    raw_id_fields = ["company", "address_type"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Standalone administration for multi-channel operational contact records."""
    list_display = ["company", "channel", "usage", "value", "is_primary", "is_verified"]
    list_filter = ["channel", "usage", "is_primary", "is_verified"]
    search_fields = ["company__name", "value", "notes"]
    raw_id_fields = ["company"]
 
