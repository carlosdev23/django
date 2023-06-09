from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField(_('name'), max_length=254)
    country = CountryField(_('country'), )
    created_on = models.DateField(auto_now_add=True, editable=False)

    auto_create_schema = True

    @property
    def primary_domain(self):
        return self.get_primary_domain()


class Domain(DomainMixin):
    pass
