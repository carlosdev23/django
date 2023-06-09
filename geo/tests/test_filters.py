from datetime import datetime
from django_tenants.test.cases import TenantTestCase

from geo.models import Powerline
from geo.tests.factories import PowerlineFactory
from geo.filters import PowerlineFilter

from projects.tests.factories import ProjectFactory

from django.contrib.gis.geos import GEOSGeometry


class PowerlinesFilterTest(TenantTestCase):
    def setUp(self):

        super().setUp()

        geometry = GEOSGeometry(
            str(
                {
                    "type": "LineString",
                    "coordinates": [
                        [36.71352982521057, 34.72262901747836],
                        [36.71555757522583, 34.72299056435158],
                    ],
                }
            )
        )

        self.project = ProjectFactory(name="test project")
        self.powerline = PowerlineFactory(
            properties={
                "id": 1,
                "surrounding_data": {"area": 1.0},
                "intersecting_data": {"area": 2.0},
                "PRIORITY": "1 - IMMEDIATE",
            },
            project=self.project,
            geometry=geometry,
        )
        self.powerline2 = PowerlineFactory(
            project=self.project,
            properties={
                "id": 2,
                "surrounding_data": {"area": 2.0},
                "intersecting_data": {"area": 2.0},
                "PRIORITY": "None",
            },
            geometry=geometry,
        )

    def test_order_by_string_id_asc(self):
        powerline = PowerlineFilter(
            queryset=Powerline.objects.all(), data={"order_by": "string_id"}
        ).qs

        self.assertEqual(powerline[0], self.powerline)

    def test_order_by_string_id_desc(self):
        powerline = PowerlineFilter(
            queryset=Powerline.objects.all(), data={"order_by": "-string_id"}
        ).qs

        self.assertEqual(powerline[0], self.powerline2)

    def test_order_by_area_asc(self):

        powerline = PowerlineFilter(
            queryset=Powerline.objects.all(), data={"order_by": "area"}
        ).qs

        self.assertEqual(powerline[0], self.powerline)

    def test_order_by_area_desc(self):

        powerline = PowerlineFilter(
            queryset=Powerline.objects.all(), data={"order_by": "-area"}
        ).qs

        self.assertEqual(powerline[0], self.powerline2)

    def test_order_by_priority_asc(self):

        powerline = PowerlineFilter(
            queryset=Powerline.objects.all(), data={"order_by": "priority"}
        ).qs

        self.assertEqual(powerline[0], self.powerline)

    def test_order_by_priority_desc(self):

        powerline = PowerlineFilter(
            queryset=Powerline.objects.all(), data={"order_by": "-priority"}
        ).qs

        self.assertEqual(powerline[0], self.powerline2)
