from django.urls import path, include
from rest_framework_nested import routers
from .views import AnnotationModelViewSet, AnnotationPictureViewSet

app_name = 'annotations'

router = routers.DefaultRouter()
router.register('annotations', AnnotationModelViewSet)

annotations_router = routers.NestedDefaultRouter(router, 'annotations', lookup='annotation')
annotations_router.register('pictures', AnnotationPictureViewSet, basename='annotation-pictures')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(annotations_router.urls)),
]
