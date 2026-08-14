import pytest

from apps.accounts.tests.factories import DoctorProfileFactory
from apps.patients import services
from apps.patients.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestCreatePatient:
    def test_stamps_owner_ignores_spoofed_owner(self):
        real_doctor = DoctorProfileFactory()
        other_doctor = DoctorProfileFactory()

        patient = services.create_patient(
            doctor=real_doctor,
            national_id="NID-SPOOF",
            full_name="Spoof Test",
            date_of_birth="1970-01-01",
            gender="MALE",
            created_by_doctor=other_doctor,  # should be ignored
        )
        assert patient.created_by_doctor_id == real_doctor.id


class TestUpdatePatient:
    def test_update_ignores_immutable_fields(self):
        patient = PatientFactory(national_id="NID-ORIGINAL")
        other_doctor = DoctorProfileFactory()

        updated = services.update_patient(
            patient=patient,
            full_name="New Name",
            national_id="NID-CHANGED",
            created_by_doctor=other_doctor,
        )
        assert updated.full_name == "New Name"
        assert updated.national_id == "NID-ORIGINAL"
        assert updated.created_by_doctor_id != other_doctor.id


class TestArchivePatient:
    def test_archive_soft_deletes(self):
        patient = PatientFactory()
        services.archive_patient(patient=patient)
        patient.refresh_from_db()
        assert patient.is_active is False
