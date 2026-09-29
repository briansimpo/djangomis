from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse

class RoleLoginRequiredMixin(LoginRequiredMixin):
    """
    Generic mixin to enforce login and user role.
    Define allowed_roles = ["is_staff"] or ["is_client"] etc.
    """

    allowed_roles = []  # override in subclasses

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Must be authenticated
        if not user.is_authenticated:
            return redirect(reverse("account_login"))

        # If no role defined, allow only authenticated users
        if self.allowed_roles:
            # Check that at least one required role is True
            if not any(getattr(user, role, False) for role in self.allowed_roles):
                return redirect(reverse("account_login"))
        
        return super().dispatch(request, *args, **kwargs)

    def get_user(self):
        if not self.request.user.is_authenticated:
            raise Exception("User does not exist")
        return self.request.user


class StaffLoginRequired(RoleLoginRequiredMixin):
    allowed_roles = ["is_staff"]


class ClientLoginRequired(RoleLoginRequiredMixin):
    allowed_roles = ["is_client"]


class GuestLoginRequired(RoleLoginRequiredMixin):
    allowed_roles = ["is_guest"]


class RedirectAuthenticated:
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("account_redirect"))
        return super().dispatch(request, *args, **kwargs)