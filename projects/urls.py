from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectModelViewSet, MissionModelViewSet

app_name = 'projects'

router = DefaultRouter()
router.register('projects', ProjectModelViewSet)
router.register('missions', MissionModelViewSet, basename="missions")

urlpatterns = [
    path('', include(router.urls)),
]
