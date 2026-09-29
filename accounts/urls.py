from django.urls import path
from allauth.urls import urlpatterns as allauth_patterns
from . import views


urlpatterns = [
	path("signup/", views.signup, name="account_signup"),
    path("login/", views.login, name="account_login"),
    path("password/reset/", views.password_reset, name="account_reset_password"),
    path("reauthenticate/", views.reauthenticate, name="account_reauthenticate"),
    path("profile/", views.user_profile, name="account_profile"),
    path("redirect", views.account_redirect, name="account_redirect"), 
]

urlpatterns += allauth_patterns
