from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import DoctorProfile, PasswordResetCode, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "license_number", "registration_status", "reviewed_by_admin", "reviewed_at")
    list_filter = ("registration_status",)
    search_fields = ("user__username", "license_number")


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "expires_at", "created_at")
