from django.contrib import admin

from apps.reports.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "mri_scan", "created_by_doctor", "status", "finalized_at", "created_at")
    list_filter = ("status",)

    def get_queryset(self, request):
        return Report.all_objects.all()
