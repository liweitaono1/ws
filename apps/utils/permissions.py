from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication


class IsOwnerOrReadOnly(permissions.BasePermission):
    '''
    Custom permission to only allow owners of an object to edit it.
    '''

    def has_object_permission(self, request, view, obj):
        # read permissions are allowed to any request
        # so we will always allow GET,HEAD or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True
        # write permissions are only allowed to the owner of the snippet
        return obj.user == request.user


class IsOwnerOr(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return obj.authors == request.user


class IsOwnerOrRead(permissions.BasePermission):
    '''
    课程章节
    custom permission to only allow owners of an object to edit it.
    '''

    def has_object_permission(self, request, view, obj):
        # read permissions are allowed to any request
        # so we will always allow GET,HEAD or OPTIONS request
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return
        # Write permissions are only allowed to the owner of the snippet.
        return obj.course.user == request.user


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    关闭csrf验证
    """

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
