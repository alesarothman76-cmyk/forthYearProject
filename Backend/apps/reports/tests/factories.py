import factory

from apps.mri_analysis.tests.factories import MRIScanFactory
from apps.reports.models import Report, ReportStatus


class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Report

    mri_scan = factory.SubFactory(MRIScanFactory)
    created_by_doctor = factory.SelfAttribute("mri_scan.uploaded_by_doctor")
    notes = "Initial draft notes."
    status = ReportStatus.DRAFT
