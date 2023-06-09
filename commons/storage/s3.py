from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django_tenants.utils import parse_tenant_config_path


class TenantS3Storage(S3Boto3Storage):

    @property
    def location(self):
        return parse_tenant_config_path(f'{settings.AWS_LOCATION}/%s')
