from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from apps.reports.models import Report, ReportStatus


class ReportError(Exception):
    pass


def create_report(*, doctor, mri_scan, notes=""):
    return Report.objects.create(created_by_doctor=doctor, mri_scan=mri_scan, notes=notes)


def update_report_notes(*, report, notes):
    """
    FINALIZED reports are immutable - enforced here (not just in the view),
    so no code path (including a future bulk-edit script or a differently
    wired view) can bypass it.
    """
    if report.status == ReportStatus.FINALIZED:
        raise ReportError("A finalized report cannot be edited.")

    report.notes = notes
    report.save(update_fields=["notes", "updated_at"])
    return report


@transaction.atomic
def finalize_report(*, report):
    """
    Generates the PDF exactly once, at finalize-time, and transitions
    DRAFT -> FINALIZED. Calling this twice on an already-finalized report
    raises rather than silently regenerating the PDF (which would break
    the "PDF is a permanent snapshot" guarantee).
    """
    from apps.reports.pdf import generate_report_pdf  # local import avoids reportlab at module import time

    if report.status == ReportStatus.FINALIZED:
        raise ReportError("This report has already been finalized.")

    pdf_bytes = generate_report_pdf(report=report)

    report.status = ReportStatus.FINALIZED
    report.finalized_at = timezone.now()
    report.generated_pdf.save(f"report_{report.id}.pdf", ContentFile(pdf_bytes), save=False)
    report.save(update_fields=["status", "finalized_at", "generated_pdf", "updated_at"])
    return report


def archive_report(*, report):
    """
    Soft-delete. Only DRAFT reports may be archived via the normal API
    flow (enforced in the view/permission layer) - a FINALIZED report is a
    permanent medical record and is never removable through ordinary use,
    consistent with the project-wide "medical records are never
    hard-deleted" principle applied even more strictly here.
    """
    if report.status == ReportStatus.FINALIZED:
        raise ReportError("A finalized report cannot be deleted.")

    report.delete()
    return report
