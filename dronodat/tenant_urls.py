from django.urls import path, URLResolver, include
from django_tenants.urlresolvers import TenantPrefixPattern

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .base_urls import urlpatterns as base_urlpatterns

urlpatterns = base_urlpatterns + [
    path('api/v1/', include('projects.urls')),
    path('api/v1/', include('reports.urls')),
    path('api/v1/', include('geo.urls')),
    path('api/v1/', include('annotations.urls')),
]

schema_view = get_schema_view(
    openapi.Info(
        title='Dronodat Tenant API',
        default_version='v1',
        description='Full specification of Dronodat Tenant API',
        contact=openapi.Contact(email='info@dronodat.de'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[URLResolver(TenantPrefixPattern(), urlpatterns)]
)

urlpatterns = urlpatterns + [
    path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-swagger-ui-docs', ),
]
