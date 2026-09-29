from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Party, Person, Organization, Group,
    OrganizationType, LegalStructure, 
    AddressType, Address, Contact,
    RelationshipType, PartyRelationship,
    PartyRoleType, PartyRole,
    PartyTag, PartyTagAssignment
)

# =========================================================================
# SYSTEM WIDE INLINES (Tied to Core Party Node)
# =========================================================================

class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name = _("Person Profile")
    verbose_name_plural = _("Person Profiles")
    fk_name = 'party'
    extra = 0


class OrganizationInline(admin.StackedInline):
    model = Organization
    can_delete = False
    verbose_name = _("Organization Profile")
    verbose_name_plural = _("Organization Profiles")
    fk_name = 'party'
    extra = 0


class GroupInline(admin.StackedInline):
    model = Group
    can_delete = False
    verbose_name = _("Group Profile")
    verbose_name_plural = _("Group Profiles")
    fk_name = 'party'
    extra = 0


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fields = ('address_type', 'line1', 'city', 'country', 'is_primary')
    classes = ('collapse',)  # Keeps UI clean unless expanded


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ('channel', 'usage', 'value', 'is_primary', 'is_verified')
    classes = ('collapse',)


class PartyRoleInline(admin.TabularInline):
    model = PartyRole
    extra = 1
    fields = ('role_type', 'start_date', 'end_date', 'is_active')


class PartyTagAssignmentInline(admin.TabularInline):
    model = PartyTagAssignment
    extra = 1

# =========================================================================
# CORE IDENTITY MANAGERS
# =========================================================================

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ( 'party_type', 'is_active', 'created')
    list_filter = ('party_type', 'is_active', 'created')
    search_fields = ('code', 'person_profile__first_name', 'person_profile__last_name', 'organization_profile__name')
    ordering = ('-created',)
    readonly_fields = ('created', 'modified')
    
    # The absolute command center aggregation
    inlines = [
        PersonInline, 
        OrganizationInline, 
        GroupInline,
        AddressInline, 
        ContactInline, 
        PartyRoleInline, 
        PartyTagAssignmentInline
    ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'party', 'id_type', 'id_number', 'gender', 'date_of_birth')
    list_filter = ('gender', 'marital_status', 'id_type', 'blood_type')
    search_fields = ('first_name', 'middle_name', 'last_name', 'id_number', 'party__code')
    readonly_fields = ('created', 'modified')
    
    @admin.display(description=_("Full Name"), ordering='last_name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"



@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'org_type', 'legal_structure', 'tax_number')
    list_filter = ('org_type', 'legal_structure', 'fiscal_year_end_month')
    search_fields = ('name', 'trade_name', 'registration_number', 'tax_number', 'party__code')
    readonly_fields = ('created', 'modified')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'group_type')
    list_filter = ('group_type',)
    search_fields = ('name', 'group_type', 'party__code')
    readonly_fields = ('created', 'modified')


# =========================================================================
# GRAPH GRAPH & COMMUNICATION LOGISTICS MANAGERS
# =========================================================================

@admin.register(PartyRelationship)
class PartyRelationshipAdmin(admin.ModelAdmin):
    list_display = ('source_party', 'relationship_type', 'target_party', 'is_active', 'start_date', 'end_date')
    list_filter = ('relationship_type', 'is_active', 'start_date')
    # Using autocomplete_fields prevents administrative lag when database scales to millions of records
    autocomplete_fields = ['source_party', 'target_party']
    readonly_fields = ('created', 'modified')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('party', 'address_type', 'city', 'country', 'is_primary')
    list_filter = ('address_type', 'country', 'is_primary')
    search_fields = ('line1', 'city', 'region', 'postal_code', 'party__code')
    autocomplete_fields = ['party']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('party', 'channel', 'usage', 'value', 'is_primary', 'is_verified')
    list_filter = ('channel', 'usage', 'is_primary', 'is_verified')
    search_fields = ('value', 'notes', 'party__code')
    autocomplete_fields = ['party']

# =========================================================================
# ADMINISTRATIVE OPTION/LOOKUP MANAGERS (Standardized Boilerplate)
# =========================================================================

class BaseOptionAdmin(admin.ModelAdmin):
    """Reusable admin base class for dynamic metadata configurations."""
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(OrganizationType)
class OrganizationTypeAdmin(BaseOptionAdmin):
    pass


@admin.register(LegalStructure)
class LegalStructureAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created')
    search_fields = ('code', 'name')
    readonly_fields = ('created', 'modified')


@admin.register(AddressType)
class AddressTypeAdmin(BaseOptionAdmin):
    pass


@admin.register(RelationshipType)
class RelationshipTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'inverse_name')
    search_fields = ('code', 'name', 'inverse_name')


@admin.register(PartyRoleType)
class PartyRoleTypeAdmin(BaseOptionAdmin):
    pass


@admin.register(PartyTag)
class PartyTagAdmin(BaseOptionAdmin):
    pass