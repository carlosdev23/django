from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .base_urls import urlpatterns as base_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title='Dronodat Staff API',
        default_version='v1',
        description='Full specification of Dronodat Staff API',
        contact=openapi.Contact(email='info@dronodat.de'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    urlconf=settings.PUBLIC_SCHEMA_URLCONF,
)

urlpatterns = base_urlpatterns + [
    re_path(r'^api/v1/', include('clients.urls')),
    path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-swagger-ui-docs', ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
