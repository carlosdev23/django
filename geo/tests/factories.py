from datetime import datetime
import factory

from geo.models import Powerline


class PowerlineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Powerline

    properties = {
        "id": 1,
        "surrounding_data": {"area": 1.0},
        "intersecting_data": {"area": 2.0},
        "PRIORITY": "1 - IMMEDIATE",
    }
