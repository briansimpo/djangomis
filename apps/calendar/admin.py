from django.contrib import admin
from .models import (
    CalendarType,
    CalendarPeriod,
    Activity,
    Schedule,
    Holiday,
)


@admin.register(CalendarType)
class CalendarTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default")
    list_filter = ("is_default",)
    search_fields = ("name",)


class CalendarPeriodInline(admin.TabularInline):
    model = CalendarPeriod
    fk_name = "parent"
    extra = 0


@admin.register(CalendarPeriod)
class CalendarPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "calendar_type",
        "org_unit",
        "start_year",
        "start_month",
        "end_year", 
        "end_month",
        "is_open",
        "is_current",
        "parent"
    )
    list_filter = (
        "calendar_type",
        "org_unit",
        "is_open",
        "is_current",
        "start_year",
    )
    search_fields = ("name",)
    autocomplete_fields = ("calendar_type", "org_unit", "parent")
    inlines = [CalendarPeriodInline]

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "calendar_type", "org_unit", "parent")
        }),
        ("Start Date", {
            "fields": ("start_year", "start_month", "start_day")
        }),
        ("End Date", {
            "fields": ("end_year", "end_month", "end_day")
        }),
        ("Status", {
            "fields": ("is_open", "is_current")
        }),
        ("Extra", {
            "fields": ("metadata",)
        }),
    )


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("name",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "period",
        "activity",
        "start_date",
        "end_date",
        "is_open",
    )
    list_filter = ("is_open", "activity", "period")
    search_fields = ("period__name", "activity__name")
    autocomplete_fields = ("period", "activity")

    fieldsets = (
        ("Core", {
            "fields": ("period", "activity")
        }),
        ("Dates", {
            "fields": ("start_date", "end_date")
        }),
        ("Status", {
            "fields": ("is_open",)
        }),
        ("Extra", {
            "fields": ("metadata",)
        }),
    )



@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "calendar_type",
        "period",
        "start_date",
        "end_date",
        "is_recurring",
        "is_public_holiday",
    )
    list_filter = (
        "calendar_type",
        "period",
        "is_recurring",
        "is_public_holiday",
        "is_working_day",
        "recurrence_type",
    )
    search_fields = ("name", "description")
    autocomplete_fields = ("calendar_type", "period")

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "description")
        }),
        ("Scope", {
            "fields": ("calendar_type", "period")
        }),
        ("Dates", {
            "fields": ("start_date", "end_date")
        }),
        ("Recurrence", {
            "fields": ("is_recurring", "recurrence_type", "month", "day")
        }),
        ("Classification", {
            "fields": ("is_public_holiday", "is_working_day")
        }),
        ("Extra", {
            "fields": ("metadata",)
        }),
    )