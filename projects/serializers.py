from typing import List
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from geo.models import Geo3DLocation, Powerline
from .models import Project, Mission, BaseWorkFLow


class UserSummary(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'name',)

    def to_internal_value(self, data):
        try:
            return get_user_model().objects.get(pk=int(data))
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(f"Invalid pk \"{data}\" - object does not exist.")
        except (ValueError, TypeError):
            raise serializers.ValidationError(f"Invalid pk \"{data}\".")


class ProjectSummarySerializer(serializers.Serializer):
    missions = serializers.DictField(child=serializers.IntegerField(help_text='missions\'s count'),
                                     help_text='keys represent possible mission status')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class WorkflowSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(BaseWorkFLow.StatusChoices.choices, required=False,
                                     help_text=f'{BaseWorkFLow.StatusChoices.choices}')
    assignees = UserSummary(many=True)

    class Meta:
        model = BaseWorkFLow
        fields = '__all__'
        read_only_fields = ('created_on',)

    def create(self, validated_data):
        assignees = validated_data.pop('assignees', [])
        status = validated_data.pop('status', BaseWorkFLow.StatusChoices.PENDING.value)

        if status != BaseWorkFLow.StatusChoices.PENDING.value:
            raise serializers.ValidationError(f'{status=} not allowed on creation.')

        instance = super(WorkflowSerializer, self).create(validated_data)

        if assignees:
            instance.assignees.set(assignees)

        return instance

    def update(self, instance, validated_data):
        assignees = validated_data.pop('assignees', [])

        if status := validated_data.pop('status', None):
            instance.update_status(status)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if assignees:
            instance.assignees.set(assignees)

        return instance


class ProjectSerializer(WorkflowSerializer):
    contact_person = UserSummary(allow_null=True)
    summary = serializers.SerializerMethodField(read_only=True, )

    class Meta(WorkflowSerializer.Meta):
        model = Project

    @swagger_serializer_method(serializer_or_field=ProjectSummarySerializer)
    def get_summary(self, instance: Project):
        return {
            'missions': {
                Mission.StatusChoices.PENDING: instance.pending_missions.count(),
                Mission.StatusChoices.IN_PROCESS: instance.under_processing_missions.count(),
                Mission.StatusChoices.DONE: instance.completed_missions.count(),
            }
        }


class MissionSerializer(WorkflowSerializer):
    type = serializers.ChoiceField(Mission.TypeChoices.choices, required=True,
                                   help_text=f'{Mission.TypeChoices.choices}')

    geo_2d_locations = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Powerline.objects.all())

    geo_3d_locations = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Geo3DLocation.objects.all())

    class Meta(WorkflowSerializer.Meta):
        model = Mission

    def validate_project(self, project):
        if self.instance and self.instance.project_id != project.id:
            raise serializers.ValidationError("project can't be modified after creation")

        return project

    def validate_geo_2d_locations(self, locations):
        return self._validate_locations(locations)

    def validate_geo_3d_locations(self, locations):
        return self._validate_locations(locations)

    def _validate_locations(self, locations: List):
        allowed_values = [None, self.instance.pk] if self.instance else [None, ]
        if len([location for location in locations if location.mission_id not in allowed_values]) >= 1:
            raise serializers.ValidationError('One or more locations are already assigned to other missions')
        return locations

    def create(self, validated_data):
        update_locations = self._read_then_update_locations(validated_data)
        mission = super(MissionSerializer, self).create(validated_data)
        
        update_locations(mission)
        mission.send_mission_email_notification()
        return mission

    def update(self, instance, validated_data):
        update_locations = self._read_then_update_locations(validated_data)
        mission = super(MissionSerializer, self).update(instance, validated_data)
        if self.context['request'].data.get('send_email'):
            mission.send_mission_email_notification('update')
        update_locations(mission)
       
        return mission
        

    @classmethod
    def _read_then_update_locations(cls, validated_data):
        geo_2d_locations = validated_data.pop('geo_2d_locations', None)
        geo_3d_locations = validated_data.pop('geo_3d_locations', None)

        def update_locations(mission):
            if geo_2d_locations:
                mission.geo_2d_locations.set(geo_2d_locations)

            if geo_3d_locations:
                mission.geo_3d_locations.set(geo_3d_locations)

        return update_locations
