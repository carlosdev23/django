from collections import Counter

from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Area
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Sum, Count

from geo.managers import GeoLocationManager, PowerlineManager


def default_map_view_center():
    return Point(*settings.DEFAULT_MAP_VIEW_CONFIG['center'])


def default_map_view_zoom():
    return settings.DEFAULT_MAP_VIEW_CONFIG['zoom']


class MapViewConfiguration(models.Model):
    center = models.PointField(default=default_map_view_center)
    zoom = models.PositiveSmallIntegerField(default=default_map_view_zoom)

    def save(self, *args, **kwargs):
        if not self.pk and MapViewConfiguration.objects.exists():
            raise ValidationError(f'There can be only one instance of {self.__class__.__name__}')

        return super(MapViewConfiguration, self).save(*args, **kwargs)


class BaseGeoLocation(models.Model):

    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE, null=True)

    properties = models.JSONField()
    
    objects = GeoLocationManager()

    @classmethod
    def get_geojson_mapping(self):
        return {
            'properties': 'properties',
            'geometry': 'geometry',
        }

    class Meta:
        abstract = True


class Geo2DLocation(BaseGeoLocation):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='geo_2d_locations')
    mission = models.ForeignKey('projects.Mission', on_delete=models.CASCADE, null=True,
                                related_name='geo_2d_locations')
    geometry = models.GeometryField(dim=2, geography=True)


class Geo3DLocation(BaseGeoLocation):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='geo_3d_locations')
    mission = models.ForeignKey('projects.Mission', on_delete=models.CASCADE, null=True,
                                related_name='geo_3d_locations')
    geometry = models.GeometryField(dim=3, geography=True)


class Powerline(Geo2DLocation):
    objects = PowerlineManager()

    class Meta:
        proxy = True

    def update_neighbours_data(self, poly_2d_location_queryset, commit=True):
        poly_2d_location_queryset = poly_2d_location_queryset.annotate(area_=Area('geometry'))

        self.update_intersecting_data(poly_2d_location_queryset)
        self.update_surrounding_data(poly_2d_location_queryset)

        if commit:
            self.save(update_fields=['properties'])

    def update_intersecting_data(self, poly_2d_location_queryset):
        intersecting = poly_2d_location_queryset.filter(geometry__intersects=self.geometry)
        summary = intersecting.aggregate(total_area=Sum('area_', default=0), total_count=Count('pk'))
        intersecting_data = Counter(self.properties.get('intersecting_data', {}))
        intersecting_data.update(area=summary['total_area'].sq_m, count=summary['total_count'])
        self.properties['intersecting_data'] = intersecting_data

    def update_surrounding_data(self, poly_2d_location_queryset):
        surrounding_polygons = poly_2d_location_queryset \
            .filter(geometry__distance_lte=(self.geometry, D(m=6)))

        results = surrounding_polygons.values('properties__PRIORITY') \
            .annotate(total_area=Sum('area_', default=0), total_count=Count('properties__PRIORITY'))

        surrounding_data = Counter(self.properties.get('surrounding_data', {}))
        surrounding_data_per_priority = self.properties.get('surrounding_data_per_priority', {})

        for row in results:
            priority = row['properties__PRIORITY']
            priority_data = Counter(surrounding_data_per_priority.get(priority, {}))
            update_data = dict(count=row['total_count'], area=row['total_area'].sq_m)
            priority_data.update(update_data)
            surrounding_data.update(update_data)
            surrounding_data_per_priority[priority] = priority_data

        
        keys = surrounding_data_per_priority.keys()
        priority = 'None'
        if '01 - Immediate' in keys:
            priority = '01 - Immediate'
        elif '1M - 1 Month' in keys:
            priority = '1M - 1 Month'
        elif '3M - 3 Months' in keys:
            priority = '3M - 3 Months'
        
        self.properties['PRIORITY_ORG'] =  self.properties.get('PRIORITY', 'None')
        self.properties['PRIORITY'] = priority


        self.properties['surrounding_data_per_priority'] = surrounding_data_per_priority
        self.properties['surrounding_data'] = surrounding_data
