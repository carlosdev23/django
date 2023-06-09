from django.contrib.gis.db import models


class GeometryType(models.Func):
    function = 'GeometryType'
    output_field = models.CharField()