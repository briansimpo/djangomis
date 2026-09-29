from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm



class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"), 
            {
                "fields": (
                    "first_name", 
                    "last_name",
                )
            }
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_guest",
                    "is_staff",
                    "is_client",
                    "is_superuser",
                    "is_first_login",
                    "groups",
                    "user_permissions"
                ),
            },
        ),
        (
            _("Important dates"), 
            {
                "fields": (
                    "last_login", 
                    "date_joined"
                )
            }
        ),
    )
    list_display = ["email", "first_name", "last_name",  "is_staff", "is_client", "is_active"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
        
        
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
       

admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
