from django_tenants.utils import get_public_schema_name


def is_request_for_client(request):
    return not is_request_for_dronodat_client(request)


def is_request_for_dronodat_client(request):
    return request.tenant.name == 'public'


def is_user_staff(request):
    return request.user.client.schema_name == get_public_schema_name()
