from rest_framework import serializers

from annotations.models import Annotation, AnnotationPicture


class AnnotationPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationPicture
        fields = ('id', 'picture', 'created_on',)
        read_only_fields = ('created_on',)


class AnnotationSerializer(serializers.ModelSerializer):
    pictures = AnnotationPictureSerializer(many=True, read_only=True)

    class Meta:
        model = Annotation
        fields = '__all__'
        read_only_fields = ('creator', 'created_on',)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['creator'] = request.user
        return super(AnnotationSerializer, self).create(validated_data)

    def validate_mission(self, mission):
        if self.instance and self.instance.mission_id != mission.id:
            raise serializers.ValidationError("mission can't be modified after creation")
        return mission
