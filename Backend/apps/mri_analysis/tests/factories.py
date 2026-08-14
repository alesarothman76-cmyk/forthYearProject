import factory
from django.core.files.base import ContentFile

from apps.accounts.tests.factories import DoctorProfileFactory
from apps.mri_analysis.models import MRIScan, ScanStatus
from apps.mri_analysis.tests.helpers import make_synthetic_png_bytes
from apps.patients.tests.factories import PatientFactory


class MRIScanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MRIScan

    patient = factory.SubFactory(PatientFactory)
    uploaded_by_doctor = factory.SubFactory(DoctorProfileFactory)
    status = ScanStatus.PENDING

    @factory.lazy_attribute
    def original_file(self):
        return ContentFile(make_synthetic_png_bytes(), name="synthetic.png")
