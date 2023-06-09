from logging import getLogger

from django.contrib.gis.db import models

from commons import db
from commons.types import GeometryType

logger = getLogger(__name__)


class GeoLocationQuerySet(models.QuerySet):
    def with_geom_type(self):
        return self.annotate(geom_type=db.GeometryType('geometry'))

    def polygons(self):
        return self.with_geom_type().filter(geom_type=GeometryType.POLYGON.label)


class GeoLocationManager(models.Manager.from_queryset(GeoLocationQuerySet)):
    pass


class PowerlineQueryset(GeoLocationQuerySet):
    def update_neighbours_data(self, poly_2d_location_queryset):
        updated = []
        for powerline in self.all():
            powerline.update_neighbours_data(poly_2d_location_queryset, commit=False)
            updated.append(powerline)

        self.bulk_update(updated, fields=['properties'], batch_size=100)


class PowerlineManager(GeoLocationManager.from_queryset(PowerlineQueryset)):
    def get_queryset(self):
        queryset = PowerlineQueryset(model=self.model, using=self._db, hints=self._hints)
        return queryset.with_geom_type().filter(geom_type=GeometryType.LINE_STRING.label)
