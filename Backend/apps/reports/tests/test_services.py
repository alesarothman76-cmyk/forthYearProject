import pytest

from apps.reports import services
from apps.reports.models import ReportStatus
from apps.reports.tests.factories import ReportFactory

pytestmark = pytest.mark.django_db


class TestUpdateReportNotes:
    def test_updates_draft_report(self):
        report = ReportFactory(status=ReportStatus.DRAFT)
        services.update_report_notes(report=report, notes="Updated notes.")
        report.refresh_from_db()
        assert report.notes == "Updated notes."

    def test_finalized_report_cannot_be_edited(self):
        report = ReportFactory(status=ReportStatus.FINALIZED)
        with pytest.raises(services.ReportError):
            services.update_report_notes(report=report, notes="Should not apply.")


class TestFinalizeReport:
    def test_finalize_generates_pdf_and_sets_status(self):
        report = ReportFactory(status=ReportStatus.DRAFT)
        services.finalize_report(report=report)

        report.refresh_from_db()
        assert report.status == ReportStatus.FINALIZED
        assert report.finalized_at is not None
        assert report.generated_pdf.name

        report.generated_pdf.open("rb")
        try:
            content = report.generated_pdf.read()
        finally:
            report.generated_pdf.close()
        assert content.startswith(b"%PDF")

    def test_finalize_twice_raises(self):
        report = ReportFactory(status=ReportStatus.DRAFT)
        services.finalize_report(report=report)
        with pytest.raises(services.ReportError):
            services.finalize_report(report=report)


class TestArchiveReport:
    def test_archive_draft_report(self):
        report = ReportFactory(status=ReportStatus.DRAFT)
        services.archive_report(report=report)
        report.refresh_from_db()
        assert report.is_active is False

    def test_cannot_archive_finalized_report(self):
        report = ReportFactory(status=ReportStatus.FINALIZED)
        with pytest.raises(services.ReportError):
            services.archive_report(report=report)
