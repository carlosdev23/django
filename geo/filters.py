from django import forms
from django.core.exceptions import ValidationError
from django_filters import NumberFilter, CharFilter, BooleanFilter
from django.db.models.fields.json import KeyTextTransform
from django_filters.rest_framework import FilterSet
from django.db.models import ExpressionWrapper, Sum, F, FloatField
from .models import Geo3DLocation, Geo2DLocation, Powerline
from django.db.models.functions import Cast, Coalesce
from commons.types import GeometryType


def geom_type_validator(value):
    try:
        GeometryType(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid value {value} for geom_type")


class BaseGeoLocationFilter(FilterSet):
    geom_type = NumberFilter(
        method="geom_type_filter",
        help_text=f"{GeometryType.choices}",
        validators=[
            geom_type_validator,
        ],
    )

    def geom_type_filter(self, queryset, name, value):
        geo_type = GeometryType(value)
        return queryset.filter(**{name: geo_type.label})


class Geo2DLocationFilter(BaseGeoLocationFilter):
    is_assigned = BooleanFilter(
        field_name="is_assigned",
        widget=forms.HiddenInput(),
        method="filter_by_is_assigned",
    )

    def filter_by_is_assigned(self, queryset, name, value):
        return queryset.filter(mission__isnull=not value)

    class Meta:
        model = Geo2DLocation
        fields = (
            "project",
            "report",
            "mission",
        )


class Geo3DLocationFilter(BaseGeoLocationFilter):
    class Meta:
        model = Geo3DLocation
        fields = (
            "project",
            "report",
            "mission",
        )


class PowerlineFilter(FilterSet):

    order_by = CharFilter(
        widget=forms.HiddenInput(),
        method="filter_order_by",
    )

    is_assigned = BooleanFilter(
        field_name="is_assigned",
        widget=forms.HiddenInput(),
        method="filter_by_is_assigned",
    )

    def filter_order_by(self, queryset, name, value):
        if value:
            return (
                queryset.filter(id__in=queryset.values_list("id", flat=True))
                .annotate(
                    string_id=KeyTextTransform("id", "properties"),
                    intersecting_data=Cast(
                        KeyTextTransform(
                            "area", KeyTextTransform("intersecting_data", "properties")
                        ),
                        output_field=FloatField(),
                    ),
                    surrounding_data=Coalesce(
                        Cast(
                            KeyTextTransform(
                                "area",
                                KeyTextTransform("surrounding_data", "properties"),
                            ),
                            output_field=FloatField(),
                        ),
                        0.0,
                    ),
                    priority=KeyTextTransform("PRIORITY", "properties"),
                )
                .annotate(
                    area=Sum(
                        F("intersecting_data") + F("surrounding_data"),
                        output_field=FloatField(),
                    )
                )
                .order_by(value)
            )
        return queryset

    def filter_by_is_assigned(self, queryset, name, value):
        return queryset.filter(mission__isnull=not value)

    class Meta:
        model = Powerline
        fields = ["project", "report", "mission", "order_by"]
