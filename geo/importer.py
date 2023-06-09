import dataclasses
from itertools import chain
from typing import List

from django.contrib.gis.geos import GEOSGeometry

from .models import Geo2DLocation, Geo3DLocation, Powerline
from commons.types import GeometryType
from .parsers import KMLtoGeoJSONConverter


@dataclasses.dataclass
class ImportResult:
    features_count: int
    geom_type: GeometryType
    schema: List[str]


class ObjectsLoader:
    model_2d_class = Geo2DLocation
    model_3d_class = Geo3DLocation

    def load(self, geojson, report):
        self.model_objects = [self._get_object_from_feature(feature, report) for feature in geojson['features']]
        return self

    def _get_object_from_feature(self, feature, report):
        geometry = GEOSGeometry(str(feature['geometry']))
        model_class = self.model_3d_class if geometry.hasz else self.model_2d_class

        fields_mapping = model_class.get_geojson_mapping()

        params = {
            fields_mapping['properties']: feature['properties'],
            fields_mapping['geometry']: geometry,
            'project': report.project,
            'report': report
        }

        return model_class(**params)

    def persist(self):
        model_2d_objects = self._persist_objects_of_model(self.model_objects, self.model_2d_class)
        model_3d_objects = self._persist_objects_of_model(self.model_objects, self.model_3d_class)
        return model_2d_objects, model_3d_objects

    @classmethod
    def _persist_objects_of_model(cls, objects, model_class):
        objects = [obj for obj in objects if isinstance(obj, model_class)]
        return model_class.objects.bulk_create(objects, batch_size=100)


class KMLImporter:
    kml_to_geojson_converter_class = KMLtoGeoJSONConverter
    post_import_callbacks = set()

    def import_kml_report(self, report) -> ImportResult:
        converter = self.kml_to_geojson_converter_class()
        geojson = converter.convert(report.file)

        model_2d_objects, model_3d_objects = ObjectsLoader().load(geojson, report).persist()

        try:
            repr_object = next(chain(model_2d_objects, model_3d_objects))
            geom_type = self.get_object_geom_type(repr_object)
            schema = self.get_object_proprties_names(repr_object)
        except StopIteration:
            geom_type = None
            schema = []

        import_result = ImportResult(len(model_2d_objects) + len(model_3d_objects), geom_type, schema)
        self._execute_callbacks(self.post_import_callbacks, report, import_result)
        return import_result

    def get_object_geom_type(self, obj) -> GeometryType:
        try:
            return next((geom_type.value for geom_type in GeometryType if
                         geom_type.label.casefold() == obj.geometry.geom_type.casefold()))
        except StopIteration:
            pass

    def get_object_proprties_names(self, obj) -> List[str]:
        return list(obj.properties)

    @classmethod
    def on_import_finished(cls, func):
        cls.post_import_callbacks.add(func)

    @classmethod
    def _execute_callbacks(cls, callbacks, *args, **kwargs):
        for callback in callbacks:
            callback(*args, **kwargs)


@KMLImporter.on_import_finished
def update_powerline_neighbours_data(report, import_result: ImportResult):
    if import_result.geom_type in (GeometryType.POLYGON.value, GeometryType.LINE_STRING.value):
        powerline_queryset = Powerline.objects.all()
        polygon_queryset = Geo2DLocation.objects.polygons()

        if import_result.geom_type == GeometryType.POLYGON.value:
            polygon_queryset = polygon_queryset.filter(report=report)
        else:
            powerline_queryset = powerline_queryset.filter(report=report)

        powerline_queryset.update_neighbours_data(polygon_queryset)