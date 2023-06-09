from django.contrib.gis.db import models


class GeometryType(models.IntegerChoices):
    POINT = 1, 'POINT'
    LINE_STRING = 2, 'LINESTRING'
    POLYGON = 3, 'POLYGON'
    MULTI_POINT = 4, 'MULTIPOINT'
    MULTI_LINE_STRING = 5, 'MULTILINESTRING'
    MULTI_POLYGON = 6, 'MULTIPOLYGON'
