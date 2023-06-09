from rest_framework import viewsets
from django_tenants.utils import schema_context

from .models import Client
from .serializers import ClientSerializer


class ClientModelViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.exclude(name='public')
    serializer_class = ClientSerializer

    def perform_destroy(self, instance):
        with schema_context(instance.schema_name):
            return super(ClientModelViewSet, self).perform_destroy(instance)
