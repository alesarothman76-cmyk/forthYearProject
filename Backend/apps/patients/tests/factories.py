import factory

from apps.accounts.tests.factories import DoctorProfileFactory
from apps.patients.models import Gender, Patient


class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient

    national_id = factory.Sequence(lambda n: f"NID-{n:06d}")
    full_name = factory.Sequence(lambda n: f"Patient {n}")
    date_of_birth = "1960-01-01"
    gender = Gender.FEMALE
    medical_history = "No significant history."
    created_by_doctor = factory.SubFactory(DoctorProfileFactory)
