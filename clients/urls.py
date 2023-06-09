from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientModelViewSet

app_name = 'clients'

router = DefaultRouter()
router.register('clients', ClientModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
