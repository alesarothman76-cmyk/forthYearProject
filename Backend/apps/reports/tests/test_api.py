import pytest
from rest_framework import status

from apps.accounts.tests.factories import DoctorProfileFactory
from apps.mri_analysis.tests.factories import MRIScanFactory
from apps.reports.models import ReportStatus
from apps.reports.tests.factories import ReportFactory

pytestmark = pytest.mark.django_db


class TestReportCreate:
    def test_create_report_for_owned_scan(self, api_client):
        doctor = DoctorProfileFactory()
        scan = MRIScanFactory(uploaded_by_doctor=doctor)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.post("/api/reports/", {"mri_scan": scan.id, "notes": "Looks stable."}, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == ReportStatus.DRAFT
        assert response.data["created_by_doctor"] == doctor.id

    def test_create_report_for_non_owned_scan_returns_404(self, api_client):
        doctor = DoctorProfileFactory()
        other_doctor = DoctorProfileFactory()
        scan = MRIScanFactory(uploaded_by_doctor=other_doctor)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.post("/api/reports/", {"mri_scan": scan.id}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReportUpdate:
    def test_patch_notes_while_draft(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.DRAFT)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.patch(f"/api/reports/{report.id}/", {"notes": "New notes"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["notes"] == "New notes"

    def test_patch_finalized_report_returns_400(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.FINALIZED)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.patch(f"/api/reports/{report.id}/", {"notes": "New notes"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_owned_report_returns_404(self, api_client):
        doctor = DoctorProfileFactory()
        other_doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=other_doctor)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/reports/{report.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReportFinalize:
    def test_finalize_via_api(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.DRAFT)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.post(f"/api/reports/{report.id}/finalize/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == ReportStatus.FINALIZED
        assert response.data["finalized_at"] is not None

    def test_finalize_twice_returns_400(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.DRAFT)

        api_client.force_authenticate(user=doctor.user)
        api_client.post(f"/api/reports/{report.id}/finalize/")
        response = api_client.post(f"/api/reports/{report.id}/finalize/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestReportPDFDownload:
    def test_download_before_finalize_returns_400(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.DRAFT)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/reports/{report.id}/pdf/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_download_after_finalize_returns_pdf(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.DRAFT)

        api_client.force_authenticate(user=doctor.user)
        api_client.post(f"/api/reports/{report.id}/finalize/")
        response = api_client.get(f"/api/reports/{report.id}/pdf/")

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/pdf"


class TestReportDelete:
    def test_delete_draft_report(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.DRAFT)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.delete(f"/api/reports/{report.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_finalized_report_returns_400(self, api_client):
        doctor = DoctorProfileFactory()
        report = ReportFactory(created_by_doctor=doctor, status=ReportStatus.FINALIZED)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.delete(f"/api/reports/{report.id}/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestReportList:
    def test_filter_by_patient(self, api_client):
        doctor = DoctorProfileFactory()
        scan_a = MRIScanFactory(uploaded_by_doctor=doctor)
        scan_b = MRIScanFactory(uploaded_by_doctor=doctor)
        ReportFactory(created_by_doctor=doctor, mri_scan=scan_a)
        ReportFactory(created_by_doctor=doctor, mri_scan=scan_b)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/reports/?patient={scan_a.patient_id}")

        assert len(response.data) == 1
        assert response.data[0]["mri_scan"] == scan_a.id
