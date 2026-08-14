import pytest

from apps.mri_analysis.pipeline.classify import CLASS_NAMES, classify
from apps.mri_analysis.pipeline.runner import run_preprocessing
from apps.mri_analysis.tests.helpers import make_synthetic_png_bytes

# These tests need the real backbone checkpoint present at ml_models/ to
# exercise real feature extraction. They're skipped automatically if it's
# missing (see conftest skip marker below), matching Section 8.5's
# documented current real-world state.
pytestmark = pytest.mark.requires_backbone


class TestClassify:
    def test_classify_returns_full_distribution(self, mock_classifier):
        preprocess_result = run_preprocessing(make_synthetic_png_bytes())
        result = classify(preprocess_result.processed_jpeg_bytes)

        assert result.predicted_class in CLASS_NAMES
        assert set(result.class_probabilities.keys()) == set(CLASS_NAMES)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_classify_predicted_class_matches_max_probability(self, mock_classifier):
        preprocess_result = run_preprocessing(make_synthetic_png_bytes())
        result = classify(preprocess_result.processed_jpeg_bytes)

        max_class = max(result.class_probabilities, key=result.class_probabilities.get)
        assert result.predicted_class == max_class

    def test_mock_classifier_deterministic_prediction(self, mock_classifier):
        preprocess_result = run_preprocessing(make_synthetic_png_bytes())
        result = classify(preprocess_result.processed_jpeg_bytes)

        # The fake SVM in conftest.py always predicts NonDemented.
        assert result.predicted_class == "NonDemented"
        assert result.confidence_score == pytest.approx(0.80)
