# ruff: noqa: E501
from .base import *  # noqa: F403
from .api import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", True)

# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY", default="k3zPD3t6eHL07YLlS3p0oQgE7CqGmp0j2wMXXehe24LZgFMDo4b5BcAla8Tb8OiI")

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", ".localhost", "0.0.0.0", "127.0.0.1"]  # noqa: S104

# DOMAIN
# The host address where the Django application will run.
DJANGO_HOST = env("DJANGO_HOST", default="localhost")

# The port on which the Django application will listen.
DJANGO_PORT = env("DJANGO_PORT", default="8000")


DJANGO_SOCKET_HOST = env("DJANGO_SOCKET_HOST", default="localhost")
DJANGO_SOCKET_PORT = env("DJANGO_SOCKET_PORT", default="8001")

ROOT_HOSTCONF = "config.urlconf.hosts"
DEFAULT_HOST = "localhost"
PARENT_HOST = DJANGO_HOST

# Django Admin URL.
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")

# Django Vite
DJANGO_VITE = {
  "default": {
    "dev_mode": DEBUG, 
  }
}

# EMAIL CREDENTIALS
# ------------------------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST", default="mail.djangospice.com")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="noreply@djangospice.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="Ipweteka?321")


# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# SECURITY
# ------------------------------------------------------------------------------
SECURE_SSL_REDIRECT  = False

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS]

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions", "django_browser_reload"]


RECAPTCHA_ENABLED = False
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

DEFENDER_BEHIND_REVERSE_PROXY=False