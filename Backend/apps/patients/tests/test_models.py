import pytest
from django.db import IntegrityError

from apps.patients.models import Patient
from apps.patients.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestPatientSoftDelete:
    def test_delete_sets_inactive_not_removed(self):
        patient = PatientFactory()
        patient.delete()

        assert Patient.objects.filter(pk=patient.pk).count() == 0  # default manager excludes it
        assert Patient.all_objects.filter(pk=patient.pk).count() == 1  # row still exists
        patient.refresh_from_db()
        assert patient.is_active is False

    def test_national_id_unique_even_against_archived(self):
        patient = PatientFactory(national_id="NID-DUPLICATE")
        patient.delete()

        with pytest.raises(IntegrityError):
            PatientFactory(national_id="NID-DUPLICATE")
