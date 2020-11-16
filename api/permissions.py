from rest_framework import permissions
from users.models import CustomUser

class IsOwnerOrReject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(view.__dict__)
        if request.method in permissions.SAFE_METHODS and view.rater == request.user:
            return True
        return False
