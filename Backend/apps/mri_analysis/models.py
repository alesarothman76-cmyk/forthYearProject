from django.conf import settings
from django.db import models

from apps.accounts.models import DoctorProfile
from apps.common.models import TimeStampedModel
from apps.patients.models import Patient


def scan_upload_path(instance, filename):
    # Files organized per-patient in storage.
    return f"mri_scans/patient_{instance.patient_id}/original/{filename}"


def processed_upload_path(instance, filename):
    return f"mri_scans/patient_{instance.patient_id}/processed/{filename}"


class ScanStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class MRIScan(TimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="mri_scans")
    uploaded_by_doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="uploaded_scans")

    # Kept verbatim, unmodified, for audit/reprocessing.
    original_file = models.FileField(upload_to=scan_upload_path)
    # Final skull-stripped + resized JPEG.
    processed_image = models.ImageField(upload_to=processed_upload_path, null=True, blank=True)

    # Populated only for DICOM sources.
    dicom_metadata = models.JSONField(null=True, blank=True)

    # Single status field covers the ENTIRE pipeline (preprocessing AND
    # classification) after the Phase 3+4 merge - see Section 8.1.
    status = models.CharField(max_length=10, choices=ScanStatus.choices, default=ScanStatus.PENDING)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"MRIScan(id={self.id}, patient={self.patient_id}, status={self.status})"


class AIAnalysisResult(TimeStampedModel):
    """1:1 with MRIScan."""

    mri_scan = models.OneToOneField(MRIScan, on_delete=models.CASCADE, related_name="analysis_result")

    predicted_class = models.CharField(max_length=32)
    confidence_score = models.FloatField()
    # All 4 classes' probabilities, not just the top pick - deliberately
    # richer than the minimum needed, useful for future UI/analytics work.
    class_probabilities = models.JSONField()

    model_version = models.CharField(
        max_length=64, default=getattr(settings, "AI_MODEL_VERSION", "resnet50-svm-oasis-v1")
    )
    execution_time_seconds = models.FloatField()

    # Deferred - see Section 6.6. Left unpopulated until Grad-CAM proxy is
    # built and signed off.
    heatmap_image = models.ImageField(upload_to="heatmaps/", null=True, blank=True)

    def __str__(self):
        return f"AIAnalysisResult(scan={self.mri_scan_id}, class={self.predicted_class})"
