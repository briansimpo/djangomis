from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

from djangospice.site.routing import http_urlpatterns
from djangospice.site.utils import get_admin_app_title

admin.site.site_title = get_admin_app_title()
admin.site.site_header = get_admin_app_title()
admin.site.index_title = get_admin_app_title()


urlpatterns = [
    path("oauth/", include("oauth2_provider.urls")),
    path("defender/", include("defender.urls")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

urlpatterns += i18n_patterns(

    path(settings.ADMIN_URL, admin.site.urls),
    path("", http_urlpatterns()),  
    path("accounts/", include("accounts.urls")),
    
)


if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]

