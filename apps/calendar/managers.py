from django.db import models


class CalendarPeriodQuerySet(models.QuerySet):
    def by_org_unit(self, org_unit):
        """Filter by a specific organizational unit (accepts ID or object)."""
        if org_unit is None:
            return self.filter(org_unit__isnull=True)
        return self.filter(org_unit=org_unit)

    def by_calendar_type(self, calendar_type):
        """Filter by calendar type (accepts ID or object)."""
        return self.filter(calendar_type=calendar_type)

    def open(self):
        """Filter for periods that are currently open."""
        return self.filter(is_open=True)

    def closed(self):
        """Filter for periods that are closed."""
        return self.filter(is_open=False)


class CalendarPeriodManager(models.Manager):
    def get_queryset(self):
        return CalendarPeriodQuerySet(self.model, using=self._db)

    # Proxying these methods ensures they are available directly on the manager
    def by_org_unit(self, org_unit):
        return self.get_queryset().by_org_unit(org_unit)

    def by_calendar_type(self, calendar_type):
        return self.get_queryset().by_calendar_type(calendar_type)

    def open(self):
        return self.get_queryset().open()

    def closed(self):
        return self.get_queryset().closed()