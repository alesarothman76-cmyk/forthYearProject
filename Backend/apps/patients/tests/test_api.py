'''
D
Update tests in apps/patients/tests/test_api.py — Two tests currently expect a plain list in response.data. With pagination enabled, the response becomes a dict with count, next, previous, and results keys.

Line 61: response.data[0] → response.data["results"][0]
Line 89: response.data → response.data["results"]
3. Frontend impact — The frontend must read response.data.results and handle response.data.next / response.data.previous for navigation, instead of treating response.data as a raw array.
'''
import pytest
from rest_framework import status

from apps.accounts.tests.factories import AdminUserFactory, DoctorProfileFactory, DoctorUserFactory
from apps.patients.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestPatientOwnership:
    def test_doctor_only_sees_own_patients(self, api_client):
        doctor_a = DoctorProfileFactory()
        doctor_b = DoctorProfileFactory()
        PatientFactory(created_by_doctor=doctor_a, full_name="Alice")
        PatientFactory(created_by_doctor=doctor_b, full_name="Bob")

        api_client.force_authenticate(user=doctor_a.user)
        response = api_client.get("/api/patients/")

        assert response.status_code == status.HTTP_200_OK
        names = [p["full_name"] for p in response.data]
        assert names == ["Alice"]

    def test_non_owned_patient_returns_404_not_403(self, api_client):
        doctor_a = DoctorProfileFactory()
        doctor_b = DoctorProfileFactory()
        other_patient = PatientFactory(created_by_doctor=doctor_b)

        api_client.force_authenticate(user=doctor_a.user)
        response = api_client.get(f"/api/patients/{other_patient.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_created_by_doctor_stamped_server_side(self, api_client):
        doctor = DoctorProfileFactory()
        other_doctor = DoctorProfileFactory()
        api_client.force_authenticate(user=doctor.user)

        payload = {
            "national_id": "NID-STAMP",
            "full_name": "Stamped Patient",
            "date_of_birth": "1980-01-01",
            "gender": "MALE",
            "medical_history": "",
            "created_by_doctor": other_doctor.id,
        }
        response = api_client.post("/api/patients/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["created_by_doctor"] == doctor.id


class TestAdminPatientOversight:
    def test_admin_list_excludes_medical_history(self, api_client):
        admin = AdminUserFactory()
        PatientFactory(medical_history="Sensitive info")

        api_client.force_authenticate(user=admin)
        response = api_client.get("/api/admin/patients/")

        assert response.status_code == status.HTTP_200_OK
        assert "medical_history" not in response.data[0]

    def test_admin_cannot_patch_patient(self, api_client):
        admin = AdminUserFactory()
        patient = PatientFactory()

        api_client.force_authenticate(user=admin)
        response = api_client.patch(f"/api/admin/patients/{patient.id}/", {"full_name": "Hacked"}, format="json")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_admin_cannot_delete_patient(self, api_client):
        admin = AdminUserFactory()
        patient = PatientFactory()

        api_client.force_authenticate(user=admin)
        response = api_client.delete(f"/api/admin/patients/{patient.id}/")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_admin_sees_archived_patients_too(self, api_client):
        admin = AdminUserFactory()
        patient = PatientFactory()
        patient.delete()

        api_client.force_authenticate(user=admin)
        response = api_client.get("/api/admin/patients/")

        ids = [p["id"] for p in response.data]
        assert patient.id in ids

    def test_non_admin_forbidden(self, api_client):
        doctor = DoctorUserFactory()
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/admin/patients/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPatientHistory:
    def test_history_aggregates_scans_and_reports(self, api_client):
        from apps.mri_analysis.models import AIAnalysisResult, ScanStatus
        from apps.mri_analysis.tests.factories import MRIScanFactory
        from apps.reports.tests.factories import ReportFactory

        doctor = DoctorProfileFactory()
        patient = PatientFactory(created_by_doctor=doctor)
        scan = MRIScanFactory(uploaded_by_doctor=doctor, patient=patient, status=ScanStatus.COMPLETED)
        AIAnalysisResult.objects.create(
            mri_scan=scan,
            predicted_class="NonDemented",
            confidence_score=0.8,
            class_probabilities={"NonDemented": 0.8},
            execution_time_seconds=1.0,
        )
        ReportFactory(created_by_doctor=doctor, mri_scan=scan)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/patients/{patient.id}/history/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["patient"]["id"] == patient.id
        assert len(response.data["scans"]) == 1
        scan_data = response.data["scans"][0]
        assert scan_data["analysis_result"]["predicted_class"] == "NonDemented"
        assert len(scan_data["reports"]) == 1

    def test_history_for_non_owned_patient_returns_404(self, api_client):
        doctor = DoctorProfileFactory()
        other_doctor = DoctorProfileFactory()
        other_patient = PatientFactory(created_by_doctor=other_doctor)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/patients/{other_patient.id}/history/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_history_empty_for_patient_with_no_scans(self, api_client):
        doctor = DoctorProfileFactory()
        patient = PatientFactory(created_by_doctor=doctor)

        api_client.force_authenticate(user=doctor.user)
        response = api_client.get(f"/api/patients/{patient.id}/history/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["scans"] == []
