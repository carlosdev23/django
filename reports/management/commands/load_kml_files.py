from dataclasses import asdict

from django.core.management import BaseCommand
from django_tenants.utils import get_tenant_model, get_public_schema_name, tenant_context

from geo.importer import KMLImporter
from reports.models import Report


class Command(BaseCommand):
    def handle(self, *args, **options):
        for tenant in get_tenant_model().objects.exclude(schema_name=get_public_schema_name()):
            with tenant_context(tenant):
                self.stdout.write(f'Starting processing for tenant {tenant.name}')
                successful_import, failed_import = self._load_reports()
                self.stdout.write(f'Finished processing for tenant {tenant.name}:'
                                  f' {successful_import=}, {failed_import=}')

    def _load_reports(self):
        importer = KMLImporter()
        successful_import, failed_import = 0, 0
        for report in Report.objects.filter(type=Report.TypeChoices.KML.value, processed=False):
            try:
                import_report = importer.import_kml_report(report)
            except Exception as ex:
                report.details = {'error': str(ex)}
                failed_import += 1
            else:
                report.details = asdict(import_report)
                successful_import += 1
            finally:
                report.processed = True
                report.save()

        return successful_import, failed_import
