from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportModelViewSet,PointcloudModelViewSet
from . import views

app_name = 'reports'

router = DefaultRouter()
router.register('reports', ReportModelViewSet)
router.register('pointcloud', PointcloudModelViewSet)


urlpatterns = [
    path('', include(router.urls)),
    #path('report/all', views.test, name='all')
]
