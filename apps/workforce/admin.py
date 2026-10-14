from django.contrib import admin
from .models import (
    PositionType,
    ReportingType,
    DeploymentRole,
    Position,
    ReportingLine,
    WorkstreamType,
    Workstream,
    Worker,
    ContractType,
    Contract,
    PlacementType,
    Placement,
    Deployment,
    Supervision,
    Delegation,
)


# ============================================================
# 1. Lookup Dictionaries
# ============================================================

@admin.register(
    PositionType,
    ReportingType,
    DeploymentRole,
    WorkstreamType,
    ContractType,
    PlacementType,
)
class OptionModelAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created")
    list_filter = ("is_active",)
    search_fields = ("name",)


# ============================================================
# 2. Inlines
# ============================================================

class PlacementInline(admin.TabularInline):
    model = Placement
    extra = 0
    autocomplete_fields = (
        "position",
        "placement_type",
    )
    show_change_link = True


class DeploymentInline(admin.TabularInline):
    model = Deployment
    extra = 0
    autocomplete_fields = (
        "workstream",
        "role",
    )
    show_change_link = True


class ContractInline(admin.StackedInline):
    model = Contract
    extra = 0
    show_change_link = True


class ReportingLineInline(admin.TabularInline):
    model = ReportingLine
    fk_name = "supervisor"
    extra = 0
    autocomplete_fields = (
        "subordinate",
        "reporting_type",
    )


# ============================================================
# 3. Core Structural Models
# ============================================================

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "worker_number",
        "party",
        "is_deployable",
    )
    search_fields = (
        "worker_number",
        "party__name",
    )
    inlines = (
        ContractInline,
    )


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "status",
        "valid_from",
        "valid_until",
    )

    list_filter = (
        "status",
        "contract_type",
    )

    # Required because these are used by other admins'
    # autocomplete_fields.
    search_fields = (
        "contract_number",
        "worker__worker_number",
        "worker__party__name",
        "sponsor_party__name",
    )

    autocomplete_fields = (
        "worker",
        "sponsor_party",
        "contract_type",
    )

    inlines = (
        PlacementInline,
        DeploymentInline,
    )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "org_unit",
        "status",
    )

    list_filter = (
        "status",
        "position_type",
        "org_unit",
    )

    search_fields = (
        "code",
        "title",
    )

    inlines = (
        ReportingLineInline,
    )


@admin.register(Workstream)
class WorkstreamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "workstream_type",
        "is_active",
        "parent",
    )

    list_filter = (
        "is_active",
        "workstream_type",
    )

    search_fields = (
        "name",
    )

    inlines = (
        DeploymentInline,
    )


# ============================================================
# 4. Operational & Matrix Models
# ============================================================

@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = (
        "contract",
        "position",
        "placement_type",
        "status",
        "is_primary",
    )

    list_filter = (
        "status",
        "is_primary",
        "placement_type",
    )

    search_fields = (
        "contract__contract_number",
        "contract__worker__worker_number",
        "contract__worker__party__name",
        "position__code",
        "position__title",
    )

    autocomplete_fields = (
        "contract",
        "position",
        "placement_type",
    )

    list_select_related = (
        "contract",
        "position",
        "placement_type",
    )


@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    list_display = (
        "contract",
        "workstream",
        "role",
        "status",
        "percentage",
    )

    list_filter = (
        "status",
        "workstream",
        "role",
    )

    # Required because DelegationAdmin and SupervisionAdmin
    # reference Deployment using autocomplete_fields.
    search_fields = (
        "contract__contract_number",
        "contract__worker__worker_number",
        "contract__worker__party__name",
        "workstream__name",
        "role__name",
    )

    autocomplete_fields = (
        "contract",
        "workstream",
        "role",
    )

    list_select_related = (
        "contract",
        "workstream",
        "role",
    )


@admin.register(Supervision)
class SupervisionAdmin(admin.ModelAdmin):
    list_display = (
        "supervisor",
        "subordinate",
        "reporting_type",
    )

    search_fields = (
        "supervisor__contract__contract_number",
        "subordinate__contract__contract_number",
    )

    autocomplete_fields = (
        "supervisor",
        "subordinate",
        "reporting_type",
    )

    list_select_related = (
        "supervisor",
        "subordinate",
        "reporting_type",
    )


@admin.register(Delegation)
class DelegationAdmin(admin.ModelAdmin):
    list_display = (
        "delegator",
        "delegate",
        "delegated_role",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "delegator__contract__contract_number",
        "delegate__contract__contract_number",
        "delegated_role__name",
    )

    autocomplete_fields = (
        "delegator",
        "delegate",
        "delegated_role",
    )