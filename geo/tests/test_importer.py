from unittest.mock import patch

from django_tenants.test.cases import TenantTestCase

from geo.importer import KMLImporter
from geo.parsers import KMLtoGeoJSONConverter
from geo.tests import FIXTURES_ROOT_DIRECTORY
from geo.models import Geo2DLocation, Geo3DLocation, Powerline
from commons.types import GeometryType

from projects.models import Project
from reports.models import Report

KML_FIXTURES_ROOT_DIRECTORY = FIXTURES_ROOT_DIRECTORY / 'kml'


class KMLImporterTests(TenantTestCase):
    kml_test_files = {
        KML_FIXTURES_ROOT_DIRECTORY / '2d_polygons.kml': {
            '2d': 169,
            '3d': 0,
        },
        KML_FIXTURES_ROOT_DIRECTORY / '3d_single_polygon.kml': {
            '2d': 0,
            '3d': 1,
        },
        KML_FIXTURES_ROOT_DIRECTORY / '3d_mixed_types.kml': {
            '2d': 0,
            '3d': 19,
        },
        KML_FIXTURES_ROOT_DIRECTORY / 'empty_kml_file.kml': {
            '2d': 0,
            '3d': 0,
        }
    }

    def setUp(self):
        super(KMLImporterTests, self).setUp()
        self.project = Project.objects.create(name='test project')
        self.report = Report.objects.create(project=self.project, type=1, title='test report')

    def test_import_kml_report(self):
        importer = KMLImporter()
        for kml_file_path in self.kml_test_files.keys():
            with open(kml_file_path) as kml_file:
                self.report.file = kml_file
                importer.import_kml_report(self.report)

        self.assertEqual(Geo2DLocation.objects.count(), sum(counts['2d'] for counts in self.kml_test_files.values()))
        self.assertEqual(Geo3DLocation.objects.count(), sum(counts['3d'] for counts in self.kml_test_files.values()))

    def test_import_result(self):
        importer = KMLImporter()
        with open(KML_FIXTURES_ROOT_DIRECTORY / '2d_polygons.kml') as kml_file:
            self.report.file = kml_file
            report = importer.import_kml_report(self.report)
            self.assertEqual(report.geom_type, GeometryType.POLYGON.value)
            self.assertListEqual(
                report.schema,
                [
                    'fill-opacity', 'stroke', 'stroke-opacity', 'VEG_ID', 'PLANTNUMBE', 'COMMENTS',
                    'INSPECDATE', 'INSPECTEDB', 'DEFECTTYPE', 'PRIORITY', 'BUSHFIRERI', 'FLIGHTNUMB',
                    'FLIGHTDATE', 'PSBI', 'BUSHFIREDE', 'DEPOTID', 'NSWDEFECTC', 'VOLT_CAT', 'VEG_SPAN_I',
                    'CONDUCTOR_', 'DIST_3D', 'SPAN_LEN', 'STATION', 'TRUENORTHA', 'OWNEDBY', 'XCOORD',
                    'YCOORD', 'H_COND', 'ENCROACH', 'DEFECTS', 'VOLDEFECT', 'NUM_OH', 'CLO_OH',
                    'CAT_C_OH', 'VOL_OH', 'A1_OH', 'A2_OH', 'A3_OH', 'A4_OH', 'NUM_SITE', 'CLO_SITE',
                    'CAT_C_SITE', 'VOL_ST', 'A1_ST', 'A2_ST', 'A3_ST', 'A4_ST', 'NUM_UNDER', 'CLO_UNDER',
                    'CAT_C_UNDE', 'VOL_UG', 'A1_UG', 'A2_UG', 'A3_UG', 'A4_UG'
                ]
            )

    def test_kml_file_parsed(self):
        converter = KMLtoGeoJSONConverter()
        for kml_file_path, features_counts in self.kml_test_files.items():
            with self.subTest(file=kml_file_path):
                geojson = converter.convert(kml_file_path)
                self.assertEqual(len(geojson['features']), features_counts['2d'] + features_counts['3d'])
                self.assertIn('type', geojson)

    def test_update_powerline_neighbour_data_not_called_for_old_powerline(self):
        with patch('geo.models.Powerline.update_neighbours_data') as mocked_method:
            self._import_files('2d_polygons_frankfurt.kml', '2d_linestrings_frankfurt.kml')
            self.assertEqual(mocked_method.call_count, 3)
            self._import_files('2d_single_linestring_frankfurt.kml')
            self.assertEqual(mocked_method.call_count, 4)

    def test_update_intersecting_data__when_polygons_imported_first(self):
        self._import_files('2d_polygons_frankfurt.kml', '2d_linestrings_frankfurt.kml')
        self._assert_powerline_intersecting_data_updated()

    def test_update_intersecting_data__when_polygons_imported_second(self):
        self._import_files('2d_linestrings_frankfurt.kml', '2d_polygons_frankfurt.kml')
        self._assert_powerline_intersecting_data_updated()

    def test_update_surrounding_data(self):
        self._import_files('2d_linestring_6_polygons_with_priority.kml', '2d_2_polygons_with_priority.kml')
        expected_surrounding_data = {
            '1M': {
                'count': 3,
                'area': 263.07,

            },
            '2M': {
                'count': 3,
                'area': 302.70,
            },
            '3M': {
                'count': 1,
                'area': 42.51,
            }
        }
        powerline = Powerline.objects.first()

        self.assertEqual(powerline.properties['surrounding_data']['count'], 7)
        self.assertAlmostEqual(powerline.properties['surrounding_data']['area'], 608.28, delta=608.28 * 0.01)
        self.assertEqual(len(powerline.properties['surrounding_data_per_priority']), 3)

        for priority, data in expected_surrounding_data.items():
            saved_priority_data = powerline.properties['surrounding_data_per_priority'][priority]
            self.assertAlmostEqual(saved_priority_data['area'], data['area'], delta=data['area'] * 0.01)
            self.assertEqual(saved_priority_data['count'], data['count'])

    def _import_files(self, *files):
        importer = KMLImporter()
        for file in files:
            with open(KML_FIXTURES_ROOT_DIRECTORY / file) as kml_file:
                report = Report.objects.create(project=self.project, type=1, title='other test report')
                report.file = kml_file
                importer.import_kml_report(report)

    def _assert_powerline_intersecting_data_updated(self):
        first_powerline = Powerline.objects.get(properties__name='first')
        self.assertEqual(first_powerline.properties['intersecting_data']['count'], 2)
        self.assertAlmostEqual(first_powerline.properties['intersecting_data']['area'], 19888.47, delta=19888.47 * 0.01)

        first_powerline = Powerline.objects.get(properties__name='second')
        self.assertEqual(first_powerline.properties['intersecting_data']['count'], 1)
        self.assertAlmostEqual(first_powerline.properties['intersecting_data']['area'], 2951.29, delta=2951.29 * 0.01)

        first_powerline = Powerline.objects.get(properties__name='third')
        self.assertEqual(first_powerline.properties['intersecting_data']['count'], 1)
        self.assertAlmostEqual(first_powerline.properties['intersecting_data']['area'], 11732.44, delta=11732.44 * 0.01)
