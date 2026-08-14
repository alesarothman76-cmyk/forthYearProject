import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from apps.accounts.tests.factories import DoctorProfileFactory
from apps.mri_analysis.tests.factories import MRIScanFactory
from apps.mri_analysis.tests.helpers import make_synthetic_png_bytes
from apps.patients.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestMRIScanUpload:
    def test_upload_for_non_owned_patient_returns_404(self, api_client):
        doctor = DoctorProfileFactory()
        other_doctor = DoctorProfileFactory()
        other_patient = PatientFactory(created_by_doctor=other_doctor)

        api_client.force_authenticate(user=doctor.user)
        uploaded_file = SimpleUploadedFile("scan.png", make_synthetic_png_bytes(), content_type="image/png")
        response = api_client.post(
            "/api/mri-scans/", {"patient": other_patient.id, "file": uploaded_file}, format="multipart"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_runs_pipeline_and_returns_scan(self, api_client):
        doctor = DoctorProfileFactory()
        patient = PatientFactory(created_by_doctor=doctor)

        api_client.force_authenticate(user=doctor.user)
        uploaded_file = SimpleUploadedFile("scan.png", make_synthetic_png_bytes(), content_type="image/png")
        response = api_client.post("/api/mri-scans/", {"patient": patient.id, "file": uploaded_file}, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        # Real environment result depends on whether ml_models/ artifacts
        # are present - either way, status is never a silent success/500.
        assert response.data["status"] in ("COMPLETED", "FAILED")


class TestMRIScanList:
    def test_doctor_only_sees_own_scans(self, api_client):
        doctor_a = DoctorProfileFactory()
        doctor_b = DoctorProfileFactory()
        MRIScanFactory(uploaded_by_doctor=doctor_a)
        MRIScanFactory(uploaded_by_doctor=doctor_b)

        api_client.force_authenticate(user=doctor_a.user)
        response = api_client.get("/api/mri-scans/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_by_patient(self, api_client):
        doctor = DoctorProfileFactory()
        patient = PatientFactory(created_by_doctor=doctor)
        other_patient = PatientFactory(created_by_doctor=doctor)
        MRIScanFactory(uploaded_by_doctor=doctor, patient=patient)
        MRIScanFactory(uploaded_by_doctor=doctor, patient=other_patient)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/mri-scans/?patient={patient.id}")

        assert len(response.data) == 1
        assert response.data[0]["patient"] == patient.id


class TestMRIScanDetail:
    def test_includes_nested_analysis_result(self, api_client):
        from apps.mri_analysis.models import AIAnalysisResult, ScanStatus

        doctor = DoctorProfileFactory()
        scan = MRIScanFactory(uploaded_by_doctor=doctor, status=ScanStatus.COMPLETED)
        AIAnalysisResult.objects.create(
            mri_scan=scan,
            predicted_class="NonDemented",
            confidence_score=0.8,
            class_probabilities={"NonDemented": 0.8},
            execution_time_seconds=1.0,
        )

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/mri-scans/{scan.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["analysis_result"]["predicted_class"] == "NonDemented"

    def test_non_owned_scan_returns_404(self, api_client):
        doctor = DoctorProfileFactory()
        other_doctor = DoctorProfileFactory()
        scan = MRIScanFactory(uploaded_by_doctor=other_doctor)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/mri-scans/{scan.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
