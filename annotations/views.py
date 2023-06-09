from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.parsers import MultiPartParser

from .models import Annotation, AnnotationPicture
from .permissions import IsPictureAnnotationCreator, IsAnnotationCreator, IsAssignedToMissionOrToMissionProject
from .serializers import AnnotationSerializer, AnnotationPictureSerializer


class AnnotationModelViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationSerializer
    queryset = Annotation.objects.all()

    filterset_fields = ['mission', 'creator', ]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(
            Q(mission__in=self.request.user.missions.all()) |
            Q(mission__project__in=self.request.user.projects.all())) \
            .distinct()

    def get_permissions(self):
        permissions = super(AnnotationModelViewSet, self).get_permissions()
        return permissions + [IsAnnotationCreator(), IsAssignedToMissionOrToMissionProject()]


class AnnotationPictureViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin,
                               viewsets.GenericViewSet):
    serializer_class = AnnotationPictureSerializer
    queryset = AnnotationPicture.objects.all()

    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        return AnnotationPicture.objects.filter(annotation_id=self.kwargs['annotation_pk'])

    def perform_create(self, serializer):
        serializer.save(annotation_id=self.kwargs['annotation_pk'])

    def get_permissions(self):
        permissions = super(AnnotationPictureViewSet, self).get_permissions()
        return permissions + [IsPictureAnnotationCreator()]
