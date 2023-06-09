from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupModelViewSet, PermissionModelViewSet, UserModelViewSet, SearchUsersListAPIView

app_name = 'users'

router = DefaultRouter()
router.register('groups', GroupModelViewSet)
router.register('permissions', PermissionModelViewSet)
router.register('users', UserModelViewSet)

urlpatterns = [
    path('users/search/', SearchUsersListAPIView.as_view()),
    path('', include(router.urls)),
]
