from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"

class IsWorker(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "worker"

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"
