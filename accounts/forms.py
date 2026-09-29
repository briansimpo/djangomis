from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm as AllauthSignupForm
from allauth.account.forms import LoginForm as AllauthLoginForm
from allauth.account.forms import ResetPasswordForm as AllauthResetPasswordForm
from allauth.account.forms import ReauthenticateForm as AllauthReauthenticateForm
from allauth.socialaccount.forms import SignupForm as AllauthSocialSignupForm
from allauth.account.forms import PasswordField
from allauth.utils import set_form_field_order
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import  ReCaptchaV3

User = get_user_model()

recaptcha_enabled = getattr(settings, "RECAPTCHA_ENABLED")


class SignupForm(AllauthSignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """
    

    field_order = [
        "email",
        "password1",
        "password2",
        "captcha",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"] = PasswordField(
            label="Password",
            autocomplete="new-password",
        )
        self.fields["password2"] = PasswordField(
            label="Password (again)", autocomplete="new-password"
        )

        if recaptcha_enabled:
            self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV3)

        set_form_field_order(self, self.field_order)
        
    def save(self, request):
        # Call the parent save method to create the user instance
        user = super().save(request)
        
        # Set your custom field
        user.is_guest = True
        
        # Save the updated user instance
        user.save()
        
        return user


class SocialSignupForm(AllauthSocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
    
    def save(self, request):
        # The super().save(request) handles the social account linking
        user = super().save(request)
        
        # Flag the social user as a guest
        user.is_guest = True
        user.save()
        
        return user
    

class LoginForm(AllauthLoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].help_text = None

        if recaptcha_enabled:
            self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV3)


class ResetPasswordForm(AllauthResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if recaptcha_enabled:
            self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV3)


class ReauthenticateForm(AllauthReauthenticateForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if recaptcha_enabled:
            self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV3)