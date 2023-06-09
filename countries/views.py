from django_countries import countries
from rest_framework.generics import ListAPIView

from .serializers import CountrySerializer


class CountryListAPIView(ListAPIView):
    queryset = countries
    serializer_class = CountrySerializer
