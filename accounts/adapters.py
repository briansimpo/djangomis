import typing
from django.conf import settings
from django.http import HttpRequest
from allauth.socialaccount.models import SocialLogin
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from djangospice.core.mail import send_email
from djangospice.utils import safe_reverse
from users.models import User
from accounts.roles import Role   




class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(self, request: HttpRequest, sociallogin: SocialLogin, data: dict[str, typing.Any] ) -> User:
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user


class BaseAccountAdapter(DefaultAccountAdapter):
    """Common logic shared by all adapters."""

    # These can be overridden by subclasses or roles detected dynamically
    LOGIN_VIEW = "account_login"
    SIGNUP_VIEW = "account_signup"
    LOGOUT_VIEW = "account_logout"
    HOME_VIEW = "home"

    def send_mail(self, template_prefix, email, context):
        subject = f"{template_prefix}_subject.txt"
        template = f"{template_prefix}_message.txt"
        send_email(email, subject, template, context)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        user = emailconfirmation.email_address.user
        if user.socialaccount_set.exists():
            return
        super().send_confirmation_mail(request, emailconfirmation, signup)
        

    def get_email_verification_redirect_url(self, email_address):
        """
        Redirect user to the appropriate dashboard after email verification.
        """
        user = email_address.user

        # Custom role-based behavior (matches your login redirects)
        if getattr(user, "is_staff", False):
            return safe_reverse(self.HOME_VIEW, Role.staff)

        if getattr(user, "is_client", False):
            return safe_reverse(self.HOME_VIEW, Role.client)

        if getattr(user, "is_guest", False):
            return safe_reverse(self.HOME_VIEW, Role.guest)
        


class StaffAccountAdapter(BaseAccountAdapter):

    def is_open_for_signup(self, request):
        return False

    def get_login_redirect_url(self, request):
        return safe_reverse(self.HOME_VIEW, Role.staff)

    def get_logout_redirect_url(self, request):
        return safe_reverse(self.LOGIN_VIEW)


class ClientAccountAdapter(BaseAccountAdapter):

    def is_open_for_signup(self, request):
        return getattr(settings, "CLIENT_ACCOUNT_REGISTRATION", False)

    def get_login_redirect_url(self, request):
        return safe_reverse(self.HOME_VIEW, Role.client)

    def get_logout_redirect_url(self, request):
        return safe_reverse(self.LOGIN_VIEW)
    

class GuestAccountAdapter(BaseAccountAdapter):

    def is_open_for_signup(self, request):
        return getattr(settings, "GUEST_ACCOUNT_REGISTRATION", True)

    def get_login_redirect_url(self, request):
        return safe_reverse(self.HOME_VIEW, Role.guest)

    def get_logout_redirect_url(self, request):
        return safe_reverse(self.LOGIN_VIEW)
    

class AccountAdapterSelector:
    """
    A clean router that returns the correct concrete adapter based
    on schema and user role. Not a proxy, not dynamic dispatch,
    not magic. Explicit and maintainable.
    """

    def select(self, request: HttpRequest):
        """Return the correct underlying adapter."""

        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return GuestAccountAdapter(request)

        if getattr(user, "is_staff", False):
            return StaffAccountAdapter(request)

        if getattr(user, "is_client", False):
            return ClientAccountAdapter(request)

        if getattr(user, "is_guest", False):
            return GuestAccountAdapter(request)

        # Fallback
        return GuestAccountAdapter(request)


class UserAccountAdapter(DefaultAccountAdapter):
    """
    The class Allauth loads. It delegates the call to the correct
    concrete adapter selected by the router.
    """

    def _delegate(self, request: HttpRequest):
        return AccountAdapterSelector().select(request)

    def get_login_redirect_url(self, request):
        return self._delegate(request).get_login_redirect_url(request)

    def get_logout_redirect_url(self, request):
        return self._delegate(request).get_logout_redirect_url(request)

    def is_open_for_signup(self, request):
        return self._delegate(request).is_open_for_signup(request)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        return self._delegate(request).send_confirmation_mail(
            request, emailconfirmation, signup
        )

    def get_email_verification_redirect_url(self, email_address):
        request = self.request  # We attach request manually below
        return self._delegate(request).get_email_verification_redirect_url(email_address)
