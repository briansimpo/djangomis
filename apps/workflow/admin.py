from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models import (
    Workflow,
    WorkflowOutcome,
    WorkflowState,
    WorkflowAction,
    WorkflowTransition,
    WorkflowInstance,
    WorkflowTask,
    WorkflowActionLog,
    WorkflowRuleGroup,
    WorkflowRule,
    Actor,
    SLA,
)


class WorkflowOutcomeInline(admin.TabularInline):
    model = WorkflowOutcome
    extra = 0
    fields = (
        "code",
        "name",
        "description",
        "is_success",
    )


class WorkflowStateInline(admin.TabularInline):
    model = WorkflowState
    extra = 0
    fields = (
        "code",
        "name",
        "order",
        "is_initial",
        "is_terminal",
        "outcome",
    )
    autocomplete_fields = ("outcome",)
    ordering = ("order",)


class WorkflowActionInline(admin.TabularInline):
    model = WorkflowAction
    extra = 0
    fields = (
        "code",
        "name",
        "description",
    )


class WorkflowActionLogInline(admin.TabularInline):
    model = WorkflowActionLog
    extra = 0
    readonly_fields = (
        "task",
        "action",
        "from_state",
        "to_state",
        "actor",
        "comment",
        "extra_data",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ActorInline(admin.TabularInline):
    model = Actor
    extra = 0
    autocomplete_fields = (
        "worker",
        "position",
        "org_unit",
    )


class SLAInline(admin.StackedInline):
    model = SLA
    fk_name = "state"
    extra = 0
    autocomplete_fields = (
        "escalation_state",
        "escalation_user",
        "escalation_group",
    )


class WorkflowRuleInline(admin.TabularInline):
    model = WorkflowRule
    extra = 0


class WorkflowRuleGroupInline(admin.TabularInline):
    model = WorkflowRuleGroup
    extra = 0


class WorkflowTaskInline(admin.TabularInline):
    model = WorkflowTask
    extra = 0
    readonly_fields = ("started_at",)
    autocomplete_fields = (
        "assigned_to",
        "assigned_group",
        "state",
    )


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = (
        "app_label",
        "model",
    )


@admin.register(WorkflowOutcome)
class WorkflowOutcomeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_success",
    )
    list_filter = ("is_success",)
    search_fields = (
        "code",
        "name",
    )


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "is_active",
        "created",
    )
    list_filter = ("is_active",)
    search_fields = (
        "name",
        "code",
    )
    inlines = (
        WorkflowStateInline,
        WorkflowOutcomeInline,
        WorkflowActionInline,
    )


@admin.register(WorkflowState)
class WorkflowStateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "workflow",
        "order",
        "is_initial",
        "is_terminal",
        "outcome",
    )

    list_filter = (
        "workflow",
        "is_initial",
        "is_terminal",
        "can_return",
        "on_enter_enabled",
        "on_exit_enabled",
        "on_transition_enabled",
    )

    search_fields = (
        "name",
        "code",
        "workflow__name",
    )

    autocomplete_fields = ("outcome",)

    inlines = (
        ActorInline,
        SLAInline,
    )

    ordering = (
        "workflow",
        "order",
    )

    fieldsets = (
        (
            "Core Configuration",
            {
                "fields": (
                    "workflow",
                    "code",
                    "name",
                    "order",
                    "outcome",
                )
            },
        ),
        (
            "State Attributes",
            {
                "fields": (
                    "is_initial",
                    "is_terminal",
                    "can_return",
                    "can_reject",
                )
            },
        ),
        (
            "Hooks & Triggers",
            {
                "fields": (
                    "on_enter_enabled",
                    "on_exit_enabled",
                    "on_transition_enabled",
                )
            },
        ),
    )


@admin.register(WorkflowAction)
class WorkflowActionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "workflow",
    )
    list_filter = ("workflow",)
    search_fields = (
        "name",
        "code",
        "workflow__name",
    )


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = (
        "workflow",
        "from_state",
        "action",
        "to_state",
        "is_default",
    )

    list_filter = (
        "workflow",
        "is_default",
    )

    search_fields = (
        "from_state__name",
        "to_state__name",
        "action__name",
    )

    autocomplete_fields = (
        "from_state",
        "to_state",
        "action",
    )

    inlines = (WorkflowRuleGroupInline,)


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "workflow",
        "status",
        "submitted_by",
        "current_state",
        "submitted_at",
    )

    list_filter = (
        "status",
        "workflow",
        "current_state",
    )

    search_fields = (
        "object_id",
        "submitted_by__username",
        "submitted_by__email",
    )

    autocomplete_fields = (
        "workflow",
        "content_type",
        "submitted_by",
        "current_state",
        "org_unit",
    )

    inlines = (
        WorkflowTaskInline,
        WorkflowActionLogInline,
    )

    fieldsets = (
        (
            "Core Information",
            {
                "fields": (
                    "workflow",
                    "status",
                    "current_state",
                    "submitted_by",
                )
            },
        ),
        (
            "Target Object Mapping",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
        (
            "Context & Timing",
            {
                "fields": (
                    "org_unit",
                    "submitted_at",
                    "completed_at",
                )
            },
        ),
        (
            "Data",
            {
                "fields": ("metadata",)
            },
        ),
    )


@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "state",
        "status",
        "assigned_to",
        "is_breached",
    )

    list_filter = (
        "status",
        "is_breached",
        "state__workflow",
    )

    search_fields = (
        "instance__object_id",
        "assigned_to__username",
        "assigned_to__email",
    )

    autocomplete_fields = (
        "instance",
        "state",
        "assigned_to",
        "assigned_group",
    )

    date_hierarchy = "started_at"


@admin.register(WorkflowActionLog)
class WorkflowActionLogAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "action",
        "actor",
        "from_state",
        "to_state",
        "created",
    )

    list_filter = (
        "action",
        "from_state__workflow",
    )

    search_fields = (
        "instance__object_id",
        "actor__username",
        "comment",
    )

    readonly_fields = (
        "instance",
        "task",
        "action",
        "from_state",
        "to_state",
        "actor",
        "comment",
        "extra_data",
    )

    date_hierarchy = "created"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(WorkflowRuleGroup)
class WorkflowRuleGroupAdmin(admin.ModelAdmin):
    list_display = (
        "transition",
        "operator",
        "order",
    )

    list_filter = ("operator",)

    search_fields = (
        "transition__from_state__name",
    )

    autocomplete_fields = ("transition",)

    inlines = (WorkflowRuleInline,)