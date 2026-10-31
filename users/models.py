import uuid
from typing import ClassVar
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=True, unique=True)
    email = models.EmailField("Email address", unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField("First name", max_length=150, blank=True, null=True)
    last_name = models.CharField("Last name", max_length=150, blank=True, null=True)
    is_active = models.BooleanField("Account status", default=True)
    is_client = models.BooleanField("Client status", default=False)
    is_guest = models.BooleanField("Guest status", default=False)
    is_first_login = models.BooleanField(default=True)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="users",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="users",
        related_query_name="user",
    )
   
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def __str__(self) -> str:
        return f"{self.full_name} ({self.email})"
    
    @property
    def full_name(self):
        return self.get_full_name()

    def notify(self, notification):
        from djangospice.notification.notifier import Notifier
        return Notifier.send(self, notification)


