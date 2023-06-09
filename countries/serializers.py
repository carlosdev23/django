from rest_framework import serializers


class CountrySerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()

    name = serializers.CharField()
    code = serializers.CharField()
