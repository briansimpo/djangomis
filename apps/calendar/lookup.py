from djangospice.lookup.decorators import register_lookup

from .models import CalendarPeriod, CalendarType


register_lookup(CalendarPeriod, depends_on="org_unit")
register_lookup(CalendarType)
