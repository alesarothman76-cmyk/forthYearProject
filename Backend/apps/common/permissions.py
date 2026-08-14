from rest_framework.permissions import BasePermission

from apps.accounts.models import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.DOCTOR
        )


class IsActiveDoctor(IsDoctor):
    """
    The deactivation kill-switch. Checked explicitly here in addition to
    Django's own auth backend already refusing inactive users
    (defense in depth).
    """

    def has_permission(self, request, view):
        return bool(super().has_permission(request, view) and request.user.is_active)


class IsOwnerDoctor(BasePermission):
    """Object-level: compares obj.created_by_doctor_id against the requester's doctor_profile.id."""

    def has_object_permission(self, request, view, obj):
        doctor_profile = getattr(request.user, "doctor_profile", None)
        if doctor_profile is None:
            return False
        return obj.created_by_doctor_id == doctor_profile.id
