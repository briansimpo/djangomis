from rest_framework import viewsets
from django.contrib.auth.models import Group
from djangospice.rest.paginators import Pagination
from apps.users.models import User
from .serializers import UserSerializer, GroupSerializer
from .filters import UserFilter, GroupFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().prefetch_related("groups")
    serializer_class = UserSerializer
    filterset_class = UserFilter
    pagination_class = Pagination
    search_fields = ["email", "first_name", "last_name", "username"]
    ordering_fields = ["email", "is_active"]
    ordering = ["email"]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.prefetch_related("permissions")
    serializer_class = GroupSerializer
    filterset_class = GroupFilter
    pagination_class = Pagination
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]
    
