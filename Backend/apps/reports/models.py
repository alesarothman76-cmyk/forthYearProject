from django.db import models

from apps.accounts.models import DoctorProfile
from apps.common.models import SoftDeleteModel
from apps.mri_analysis.models import MRIScan


def report_pdf_upload_path(instance, filename):
    return f"reports/patient_{instance.mri_scan.patient_id}/{filename}"


class ReportStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    FINALIZED = "FINALIZED", "Finalized"


class Report(SoftDeleteModel):
    """
    A doctor-authored report against a single MRI scan's AI analysis
    result. DRAFT reports are freely editable by their owning doctor;
    FINALIZED reports are immutable (notes can no longer change, and the
    generated PDF becomes the permanent record) - enforced in services.py,
    not just at the API layer, so no code path can bypass it.
    """

    mri_scan = models.ForeignKey(MRIScan, on_delete=models.PROTECT, related_name="reports")
    created_by_doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="reports")

    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=ReportStatus.choices, default=ReportStatus.DRAFT)

    # Populated only at finalize-time - a DRAFT report has no PDF yet, so
    # nothing to download until it's finalized (finalizing IS what
    # generates it).
    generated_pdf = models.FileField(upload_to=report_pdf_upload_path, null=True, blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report(id={self.id}, scan={self.mri_scan_id}, status={self.status})"
