from django.contrib import admin

from apps.mri_analysis.models import AIAnalysisResult, MRIScan


@admin.register(MRIScan)
class MRIScanAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "uploaded_by_doctor", "status", "created_at")
    list_filter = ("status",)


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ("mri_scan", "predicted_class", "confidence_score", "model_version")
