from djangospice.lookup.decorators import register_lookup

from .models import CalendarPeriod, CalendarType


register_lookup(CalendarPeriod)
register_lookup(CalendarType)
