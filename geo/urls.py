from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Geo2DLocationViewSet, Geo3DLocationViewSet, retrieve_update_map_view_config, PowerlineViewSet

app_name = 'geo'

router = DefaultRouter()
router.register('geodata/2d', Geo2DLocationViewSet)
router.register('geodata/3d', Geo3DLocationViewSet)
router.register('powerlines', PowerlineViewSet)

urlpatterns = [
    path('map/', include(router.urls)),
    path('map/config/', retrieve_update_map_view_config),
]
