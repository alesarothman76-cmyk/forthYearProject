import pytest

from apps.reports.models import Report, ReportStatus
from apps.reports.tests.factories import ReportFactory

pytestmark = pytest.mark.django_db


class TestReportSoftDelete:
    def test_default_status_is_draft(self):
        report = ReportFactory()
        assert report.status == ReportStatus.DRAFT

    def test_delete_sets_inactive_not_removed(self):
        report = ReportFactory()
        report.delete()

        assert Report.objects.filter(pk=report.pk).count() == 0
        assert Report.all_objects.filter(pk=report.pk).count() == 1
        report.refresh_from_db()
        assert report.is_active is False
