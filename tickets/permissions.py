from rest_framework.permissions import BasePermission


def is_admin_or_operator(user):
    return user.is_superuser or user.groups.filter(name__in=['Admin', 'operator']).exists()


class IsOwnerOrAdminOperator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_admin_or_operator(request.user):
            return True
        return obj.user == request.user
