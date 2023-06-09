from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers

from .models import Geo2DLocation, Geo3DLocation, BaseGeoLocation, MapViewConfiguration, Powerline


class MapViewConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapViewConfiguration
        exclude = ('id',)


class BaseGeoLocationModelSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = BaseGeoLocation
        fields = ('id', 'project', 'mission', 'report',)
        geo_field = 'geometry'
        id_field = False

    def get_properties(self, instance: BaseGeoLocation, fields):
        properties = super(BaseGeoLocationModelSerializer, self).get_properties(instance, fields)
        return {
            **instance.properties,
            **properties
        }

    def unformat_geojson(self, feature):
        return {
            self.Meta.geo_field: feature['geometry'],
            'properties': feature['properties']
        }


class Geo2DLocationModelSerializer(BaseGeoLocationModelSerializer):
    class Meta(BaseGeoLocationModelSerializer.Meta):
        model = Geo2DLocation


class Geo3DLocationModelSerializer(BaseGeoLocationModelSerializer):
    class Meta(BaseGeoLocationModelSerializer.Meta):
        model = Geo3DLocation


class PowerlineModelSerializer(BaseGeoLocationModelSerializer):
    class Meta(BaseGeoLocationModelSerializer.Meta):
        model = Powerline
