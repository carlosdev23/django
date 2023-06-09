from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .filters import Geo2DLocationFilter, Geo3DLocationFilter, PowerlineFilter
from .models import Geo2DLocation, Geo3DLocation, MapViewConfiguration, Powerline
from .serializers import (
    Geo2DLocationModelSerializer,
    Geo3DLocationModelSerializer,
    MapViewConfigurationSerializer,
    PowerlineModelSerializer,
)


@swagger_auto_schema(
    methods=[
        "get",
    ],
    responses={200: MapViewConfigurationSerializer()},
)
@swagger_auto_schema(
    methods=[
        "put",
    ],
    request_body=MapViewConfigurationSerializer,
)
@api_view(http_method_names=["GET", "PUT"])
def retrieve_update_map_view_config(request: Request):
    map_view_conf = MapViewConfiguration.objects.first()
    if request.method == "PUT":
        serializer = MapViewConfigurationSerializer(map_view_conf, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    else:
        serializer = MapViewConfigurationSerializer(map_view_conf)
    return Response(serializer.data)


class Geo2DLocationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Geo2DLocation.objects.with_geom_type()
    serializer_class = Geo2DLocationModelSerializer

    filterset_class = Geo2DLocationFilter


class Geo3DLocationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Geo3DLocation.objects.with_geom_type()
    serializer_class = Geo3DLocationModelSerializer

    filterset_class = Geo3DLocationFilter


class PowerlineViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Powerline.objects.all()
    serializer_class = PowerlineModelSerializer

    filterset_class = PowerlineFilter
