from django.views.generic import TemplateView, RedirectView
from allauth.account.views import SignupView as AllauthSignupView
from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.views import PasswordResetView as AllauthPasswordResetView
from allauth.account.views import ReauthenticateView as AllauthReauthenticateView
from djangospice.utils import get_template_name
from .forms import LoginForm, SignupForm, ResetPasswordForm, ReauthenticateForm
from .adapters import UserAccountAdapter



class SignupView(AllauthSignupView):
    template_name = get_template_name("account/signup.html")
    form_class = SignupForm

signup = SignupView.as_view()


class LoginView(AllauthLoginView):
    template_name = get_template_name("account/login.html")
    form_class = LoginForm

      
login = LoginView.as_view()


class PasswordResetView(AllauthPasswordResetView):
    template_name = get_template_name("account/password_reset.html")
    form_class = ResetPasswordForm

password_reset = PasswordResetView.as_view()


class UserProfileView(TemplateView):
    template_name = get_template_name("account/profile.html")

user_profile = UserProfileView.as_view()


class AccountRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        
        adapter = UserAccountAdapter()
        return adapter.get_login_redirect_url(self.request)

account_redirect = AccountRedirectView.as_view()


class ReauthenticateView(AllauthReauthenticateView):
    template_name = get_template_name("account/reauthenticate.html")
    form_class = ReauthenticateForm

reauthenticate = ReauthenticateView.as_view()