import django_filters
from django.contrib.auth.models import Group
from apps.users.models import User


class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr="icontains")
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    is_client = django_filters.BooleanFilter()
    is_guest = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active", "is_staff", "is_client", "is_guest"]


class GroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    class Meta:
        model = Group
        fields = ["name"]

