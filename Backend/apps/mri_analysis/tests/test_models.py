import pytest

from apps.mri_analysis.models import AIAnalysisResult, ScanStatus
from apps.mri_analysis.tests.factories import MRIScanFactory

pytestmark = pytest.mark.django_db


class TestMRIScan:
    def test_default_status_is_pending(self):
        scan = MRIScanFactory()
        assert scan.status == ScanStatus.PENDING

    def test_failed_scan_keeps_row_with_error_message(self):
        scan = MRIScanFactory(status=ScanStatus.FAILED, error_message="Missing StandardScaler artifact.")
        assert scan.status == ScanStatus.FAILED
        assert scan.error_message


class TestAIAnalysisResult:
    def test_one_to_one_with_scan(self):
        scan = MRIScanFactory(status=ScanStatus.COMPLETED)
        result = AIAnalysisResult.objects.create(
            mri_scan=scan,
            predicted_class="NonDemented",
            confidence_score=0.8,
            class_probabilities={"NonDemented": 0.8},
            execution_time_seconds=1.2,
        )
        assert scan.analysis_result == result
