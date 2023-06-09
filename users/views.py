from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser

from clients.utils import is_request_for_dronodat_client, is_user_staff
from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    UserSerializer,
    SearchUsersResultSerializer,
)


class GroupModelViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class UserModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]
    parser_classes = (MultiPartParser,)

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    search_fields = [
        "name",
        "email",
    ]

    def get_queryset(self):
        return (
            super(UserModelViewSet, self)
            .get_queryset()
            .filter(client=self.request.tenant, is_active=True)
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class SearchUsersListAPIView(ListAPIView):
    serializer_class = SearchUsersResultSerializer
    queryset = get_user_model().objects.all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]

    search_fields = [
        "name",
        "email",
    ]

    def filter_queryset(self, queryset):
        queryset = super(SearchUsersListAPIView, self).filter_queryset(queryset)
        if is_user_staff(self.request) and not is_request_for_dronodat_client(
            self.request
        ):
            return queryset.filter(
                client__in=[self.request.tenant, self.request.user.client]
            )
        return queryset.filter(client=self.request.tenant)
