from rest_framework import permissions


class BelongToActiveTenantOrStaff(permissions.BasePermission):
    message = 'You do not have permission to perform this action in this workspace'

    def has_permission(self, request, view):
        return request.user.client_id == request.tenant.id or request.user.client.name == 'public'
