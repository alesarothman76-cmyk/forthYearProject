from django.contrib import admin

from apps.patients.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "national_id", "created_by_doctor", "is_active", "created_at")
    list_filter = ("is_active", "gender")
    search_fields = ("full_name", "national_id", "email")

    def get_queryset(self, request):
        # Admin site should see archived patients too.
        return Patient.all_objects.all()
