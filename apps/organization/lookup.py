from djangospice_lookup.decorators import register_lookup

from .models import Company, Address


register_lookup(Company)
register_lookup(Address)
