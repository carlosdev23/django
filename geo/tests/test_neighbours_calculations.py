import json

from django_tenants.test.cases import TenantTestCase

from geo.importer import ObjectsLoader
from geo.models import Geo2DLocation, Powerline
from geo.tests import FIXTURES_ROOT_DIRECTORY
from projects.models import Project
from reports.models import Report

GEO_JSON_FIXTURES_ROOT_DIRECTORY = FIXTURES_ROOT_DIRECTORY / 'geojson'


class TestMixin:
    def parse_and_create_from_geojson(self, filename):
        geojson = json.loads(open(GEO_JSON_FIXTURES_ROOT_DIRECTORY / filename).read())
        result, _ = ObjectsLoader().load(geojson, self.report).persist()
        return result


class PowerlineTestCase(TenantTestCase, TestMixin):

    def setUp(self):
        self.project = Project.objects.create(name='test project')
        self.report = Report.objects.create(project=self.project, type=1, title='test report')

    def test_update_intersecting_data__with_2_poly_1_linestring(self):
        polygons = Geo2DLocation.objects.polygons()
        self.parse_and_create_from_geojson('2_poly_1_linestring.json')

        self.assertEqual(polygons.count(), 2)
        self.assertEqual(Powerline.objects.count(), 1)

        powerline = Powerline.objects.first()
        powerline.update_neighbours_data(polygons)

        self.assertEqual(powerline.properties['intersecting_data']['count'], 2)
        self.assertAlmostEqual(powerline.properties['intersecting_data']['area'], 2611, delta=2611 * 0.01)

    def test_update_intersecting_data__with_4_poly_2_linestring(self):
        polygons = Geo2DLocation.objects.polygons()
        self.parse_and_create_from_geojson('4_poly_2_linestring.json')

        self.assertEqual(polygons.count(), 4)
        self.assertEqual(Powerline.objects.count(), 2)

        first_powerline = Powerline.objects.get(properties__name='first')
        first_powerline.update_neighbours_data(polygons)

        self.assertEqual(first_powerline.properties['intersecting_data']['count'], 4)
        self.assertAlmostEqual(first_powerline.properties['intersecting_data']['area'], 1472.22, delta=1472.22 * 0.01)

        second_powerline = Powerline.objects.get(properties__name='second')
        second_powerline.update_neighbours_data(polygons)

        self.assertEqual(second_powerline.properties['intersecting_data']['count'], 0)
        self.assertEqual(second_powerline.properties['intersecting_data']['area'], 0.00)

    def test_update_surrounding_data(self):
        polygons = Geo2DLocation.objects.polygons()
        self.parse_and_create_from_geojson('2d_linestring_6_polygons_with_priority.json')

        self.assertEqual(polygons.count(), 6)
        self.assertEqual(Powerline.objects.count(), 1)

        powerline = Powerline.objects.first()
        powerline.update_neighbours_data(polygons)

        expected_surrounding_data = {
            '1M': {
                'count': 3,
                'area': 263.07,

            },
            '2M': {
                'count': 2,
                'area': 174.3,
            }
        }

        self.assertEqual(powerline.properties['surrounding_data']['count'], 5)
        self.assertAlmostEqual(powerline.properties['surrounding_data']['area'], 437.37, delta=437.37 * 0.01)
        self.assertEqual(len(powerline.properties['surrounding_data_per_priority']), 2)

        for priority, data in expected_surrounding_data.items():
            saved_priority_data = powerline.properties['surrounding_data_per_priority'][priority]
            self.assertAlmostEqual(saved_priority_data['area'], data['area'], delta=data['area'] * 0.01)
            self.assertEqual(saved_priority_data['count'], data['count'])


class PowerlineManagerTests(TenantTestCase, TestMixin):
    def setUp(self):
        self.project = Project.objects.create(name='test project')
        self.report = Report.objects.create(project=self.project, type=1, title='test report')

    def test_update_neighbours__on_consequent_runs(self):
        polygons = Geo2DLocation.objects.polygons()
        self.parse_and_create_from_geojson('4_poly_2_linestring.json')

        first_powerline = Powerline.objects.get(properties__name='first')
        first_powerline.update_neighbours_data(polygons)

        second_powerline = Powerline.objects.get(properties__name='second')
        second_powerline.update_neighbours_data(polygons)

        new_polygons = self.parse_and_create_from_geojson('2_poly.json')

        self.assertEqual(len(new_polygons), 2)

        Powerline.objects.update_neighbours_data(
            polygons.filter(pk__in=[new_polygon.pk for new_polygon in new_polygons]))

        first_powerline.refresh_from_db()
        second_powerline.refresh_from_db()

        self.assertEqual(first_powerline.properties['intersecting_data']['count'], 5)
        self.assertAlmostEqual(first_powerline.properties['intersecting_data']['area'], 7728.72, delta=7728.72 * 0.01)

        self.assertEqual(second_powerline.properties['intersecting_data']['count'], 1)
        self.assertAlmostEqual(second_powerline.properties['intersecting_data']['area'], 1528.44, delta=1528.44 * 0.01)
