import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.tests.factories import DoctorProfileFactory
from apps.mri_analysis import services
from apps.mri_analysis.models import MRIScan, ScanStatus
from apps.mri_analysis.tests.factories import MRIScanFactory
from apps.mri_analysis.tests.helpers import make_synthetic_png_bytes
from apps.patients.tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


class TestUploadAndProcessScan:
    def test_real_upload_today_fails_at_classification_with_clear_message(self):
        """
        Real, currently-true end-to-end behavior per Section 8.5: since the
        SVM/StandardScaler .pkl files are not present, a real scan upload
        correctly completes preprocessing then fails at classification with
        status=FAILED and a clear error_message - never a silent success,
        never an unhandled 500. Intentionally NOT mocked - documents true
        current behavior. Once real .pkl files are placed at the configured
        paths, this test is expected to start failing (status becomes
        COMPLETED), which is the intended signal to update/remove it.
        """
        doctor = DoctorProfileFactory()
        patient = PatientFactory(created_by_doctor=doctor)
        uploaded_file = SimpleUploadedFile("scan.png", make_synthetic_png_bytes(), content_type="image/png")

        scan = services.upload_and_process_scan(doctor=doctor, patient=patient, uploaded_file=uploaded_file)

        assert scan.status == ScanStatus.FAILED
        assert scan.error_message  # clear, actionable message naming the missing file
        # The row is never lost even though classification failed.
        assert MRIScan.objects.filter(pk=scan.pk).exists()

    @pytest.mark.requires_backbone
    def test_upload_with_mocked_classifier_completes(self, mock_classifier):
        doctor = DoctorProfileFactory()
        patient = PatientFactory(created_by_doctor=doctor)
        uploaded_file = SimpleUploadedFile("scan.png", make_synthetic_png_bytes(), content_type="image/png")

        scan = services.upload_and_process_scan(doctor=doctor, patient=patient, uploaded_file=uploaded_file)

        assert scan.status == ScanStatus.COMPLETED
        assert scan.analysis_result.predicted_class == "NonDemented"

    def test_garbage_upload_fails_gracefully(self, mock_classifier):
        doctor = DoctorProfileFactory()
        patient = PatientFactory(created_by_doctor=doctor)
        uploaded_file = SimpleUploadedFile("garbage.bin", b"not an image", content_type="application/octet-stream")

        scan = services.upload_and_process_scan(doctor=doctor, patient=patient, uploaded_file=uploaded_file)

        assert scan.status == ScanStatus.FAILED
        assert scan.error_message
        assert MRIScan.objects.filter(pk=scan.pk).exists()


class TestReprocessScan:
    @pytest.mark.requires_backbone
    def test_reprocess_reuses_stored_original_file(self, mock_classifier):
        scan = MRIScanFactory(status=ScanStatus.FAILED, error_message="previous failure")

        services.reprocess_scan(scan=scan)

        scan.refresh_from_db()
        assert scan.status == ScanStatus.COMPLETED
