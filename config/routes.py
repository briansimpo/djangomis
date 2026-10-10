from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

from rest_framework.renderers import JSONOpenAPIRenderer
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView,SpectacularRedocView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from djangospice.site import get_admin_app_title, djangospice_urls
from djangospice.conf import DJANGOSPICE_URL

admin.site.site_title = get_admin_app_title()
admin.site.site_header = get_admin_app_title()
admin.site.index_title = get_admin_app_title()


urlpatterns = [
    path("oauth/", include("oauth2_provider.urls")),
    path("defender/", include("defender.urls")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# API URLS
urlpatterns += [
    path("api/token/", TokenObtainPairView.as_view(), name="drf-token-obtain-pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="drf-token-refresh"),
    path("api/schema/yml", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/json",SpectacularAPIView.as_view(renderer_classes=[JSONOpenAPIRenderer]),name="swagger-json",),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"),name="swagger-ui"),
    path("api/schema/docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
]


urlpatterns += i18n_patterns(

    path(settings.ADMIN_URL, admin.site.urls),
    path(DJANGOSPICE_URL, djangospice_urls()), 

    path("", include("workspace.urls")), 
    path("accounts/", include("accounts.urls")),
    path("calendar/", include("apps.calendar.urls")),
    
   
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

