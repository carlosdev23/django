import kml2geojson


class BaseKMLtoGeoJSONConverter:
    def convert(self, filepath: str):
        raise NotImplementedError()


class KMLtoGeoJSONConverter(BaseKMLtoGeoJSONConverter):

    def convert(self, kml_file):
        geojson = kml2geojson.convert(kml_file, )
        geojson, *_ = geojson
        return geojson
