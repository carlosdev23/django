from rest_framework import permissions
from rest_framework.request import Request

from annotations.models import Annotation
from projects.models import Mission


class IsAssignedToMissionOrToMissionProject(permissions.BasePermission):
    message = 'You can only add Annotation to the missions you are assigned to or to its containing projects.'

    def has_permission(self, request, view):
        if request.method == 'POST':
            mission = Mission.objects.get(pk=request.data['mission'])
            return (request.user.missions.filter(pk=mission.id).exists() or
                    request.user.projects.filter(pk=mission.project_id).exists())
        return True


class IsAnnotationCreator(permissions.BasePermission):
    message = 'You can only modify/delete Annotation you have created'

    def has_object_permission(self, request, view, obj):
        return obj.creator_id == request.user.id


class IsPictureAnnotationCreator(permissions.BasePermission):
    message = 'You can only add/delete Picture to the Annotation you have created.'

    def has_object_permission(self, request, view, obj):
        return self._is_user_owner_of_annotation(obj.annotation_id, request.user)

    def has_permission(self, request: Request, view):
        return self._is_user_owner_of_annotation(view.kwargs['annotation_pk'], request.user)

    def _is_user_owner_of_annotation(self, annotation_pk, user):
        return Annotation.objects.get(pk=annotation_pk).creator_id == user.id
