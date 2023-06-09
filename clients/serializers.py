from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from .models import Client, Domain


class ClientSerializer(serializers.ModelSerializer):
    country = CountryField()
    domain = serializers.CharField(max_length=128, source='primary_domain')

    class Meta:
        model = Client
        fields = ('id', 'name', 'country', 'created_on', 'domain',)

    def create(self, validated_data):
        domain = validated_data.pop('primary_domain')
        validated_data['schema_name'] = validated_data['name']

        client = super(ClientSerializer, self).create(validated_data)

        domain = Domain(domain=domain, is_primary=True, tenant=client, )
        domain.save()

        return client

    def update(self, client: Client, validated_data):
        domain = validated_data.pop('primary_domain')
        client: Client = super(ClientSerializer, self).update(client, validated_data)
        domain_instance: Domain = client.get_primary_domain()
        domain_instance.domain = domain
        domain_instance.save()
        return client
