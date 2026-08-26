from datetime import timedelta
from django.db import models
from djangospice.db.models import BaseModel, OptionModel
from djangospice.core.validation import has_value
from enums.datetime import Recurrence, Month
from apps.organization.models import OrgUnit
from .managers import CalendarPeriodManager



class CalendarType(OptionModel):
    is_default = models.BooleanField(default=False)


class CalendarPeriod(BaseModel):
    calendar_type = models.ForeignKey(CalendarType, on_delete=models.CASCADE, related_name="periods")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", blank=True, null=True)

    name = models.CharField(max_length=255)

    start_year = models.PositiveIntegerField(blank=True, null=True)
    start_month = models.CharField(max_length=20, choices=Month.choices, blank=True, null=True)
    start_day = models.PositiveSmallIntegerField(blank=True, null=True)
    
    end_year = models.PositiveIntegerField(blank=True, null=True)
    end_month = models.CharField(max_length=20, choices=Month.choices, blank=True, null=True)
    end_day = models.PositiveSmallIntegerField(blank=True,null=True)
    
    is_open = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    metadata = models.JSONField(default=dict, blank=True)
    org_unit = models.ForeignKey(OrgUnit, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Assign the custom manager
    objects = CalendarPeriodManager()

    class Meta:
        verbose_name = "Calendar Period"
        verbose_name_plural = "calendar periods"
        ordering = ["-start_year"]
        constraints = [
            models.UniqueConstraint(
                fields=["calendar_type", "name", "start_year"],
                name="uniq_calendar_period"
            )
        ]

    def __str__(self):
        return self.name

    @classmethod
    def get_active(cls):
        return cls.objects.open().first()
        
    @classmethod
    def get_active_list(cls):
        return cls.objects.open()


class Activity(OptionModel):
    
    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "activities"
    

class Schedule(BaseModel):
    activity = models.ForeignKey(Activity,on_delete=models.CASCADE, related_name="slots")
    period = models.ForeignKey(CalendarPeriod,on_delete=models.CASCADE, related_name="events", blank=True, null=True)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    is_open = models.BooleanField(default=False)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "schedules"
        constraints = [
            models.UniqueConstraint(
                fields=["period", "activity"],
                name="uniq_calendar_schedule"
            )
        ]

    def __str__(self):
        return f"{self.period.name} - {self.activity.name}"
    
    def iso_start_date(self):
        if has_value(self.start_date):
            return self.start_date.isoformat()
        else:
            return self.start_date
        
    def iso_end_date(self):
        if has_value(self.end_date):
            return (self.end_date + timedelta(days=1)).isoformat()
        else:
            return self.end_date


class Holiday(BaseModel):
    calendar_type = models.ForeignKey(CalendarType,on_delete=models.CASCADE,related_name="holidays",blank=True,null=True)
    period = models.ForeignKey(CalendarPeriod, on_delete=models.CASCADE, related_name="holidays", blank=True, null=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.CharField(max_length=20,blank=True,null=True, choices=Recurrence.choices)

    # For fixed annual holidays (e.g. Christmas)
    month = models.PositiveSmallIntegerField(blank=True, null=True)
    day = models.PositiveSmallIntegerField(blank=True, null=True)

    # Classification
    is_public_holiday = models.BooleanField(default=True)
    is_working_day = models.BooleanField(default=False)

    description = models.TextField(blank=True, null=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Holiday"
        verbose_name_plural = "holidays"
        ordering = ["start_date", "name"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__isnull=True) | models.Q(end_date__gte=models.F("start_date")),
                name="holiday_valid_date_range",
            )
        ]

    def __str__(self):
        if self.end_date and self.end_date != self.start_date:
            return f"{self.name} ({self.start_date} → {self.end_date})"
        return f"{self.name} ({self.start_date})"

    @property
    def duration_days(self):
        if not self.end_date:
            return 1
        return (self.end_date - self.start_date).days + 1
    
