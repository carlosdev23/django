import logging

from rest_framework import serializers

from .models import Report,Pointcloud

logger = logging.getLogger(__name__)


class ReportSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(help_text=f'{Report.TypeChoices.choices}')

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('uploaded_on', 'details', 'processed')

class PointcloudSerializer(serializers.ModelSerializer):
    #type = serializers.IntegerField(help_text=f'{Report.TypeChoices.choices}')

    class Meta:
        model = Pointcloud
        fields = '__all__'
        read_only_fields = ('uploaded_on','path','filename')