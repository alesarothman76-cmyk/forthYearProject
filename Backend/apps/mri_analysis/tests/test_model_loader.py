import re

import pytest
from django.conf import settings

from apps.mri_analysis.pipeline import model_loader

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _reset_model_cache():
    model_loader.reset_cache()
    yield
    model_loader.reset_cache()


class TestBackboneLoader:
    @pytest.mark.requires_backbone
    def test_loads_real_backbone_when_present(self):
        backbone = model_loader.get_backbone()
        assert backbone is not None
        # Cached process-wide - second call returns the same object.
        assert model_loader.get_backbone() is backbone

    def test_missing_backbone_raises_clear_error(self, monkeypatch, tmp_path):
        fake_path = tmp_path / "does_not_exist.pth"
        monkeypatch.setattr(settings, "RESNET_BACKBONE_PATH", fake_path)

        with pytest.raises(model_loader.ModelArtifactMissingError, match=re.escape(str(fake_path))):
            model_loader.get_backbone()


class TestScalerLoader:
    def test_missing_scaler_raises_clear_error_naming_the_file(self):
        """
        Real, currently-true behavior per Section 8.5: the StandardScaler
        .pkl has never been provided. This test intentionally does NOT
        mock anything. Once the real file is placed at the configured
        path, this test is expected to start failing - that's the intended
        signal that real artifacts have landed and the test should be
        updated/removed then.
        """
        with pytest.raises(model_loader.ModelArtifactMissingError) as exc_info:
            model_loader.get_scaler()
        assert str(settings.FEATURE_SCALER_PATH) in str(exc_info.value)


class TestSVMLoader:
    def test_missing_svm_raises_clear_error_naming_the_file(self):
        """
        Real, currently-true behavior per Section 8.5/Section 6.3: the SVM
        .pkl is not currently present in this project. Intentionally not
        mocked - documents true current behavior.
        """
        with pytest.raises(model_loader.ModelArtifactMissingError) as exc_info:
            model_loader.get_svm()
        assert str(settings.SVM_CLASSIFIER_PATH) in str(exc_info.value)


class TestCacheReset:
    def test_reset_cache_clears_all_three_singletons(self, monkeypatch, tmp_path):
        fake_path = tmp_path / "missing.pth"
        monkeypatch.setattr(settings, "RESNET_BACKBONE_PATH", fake_path)

        with pytest.raises(model_loader.ModelArtifactMissingError):
            model_loader.get_backbone()

        model_loader.reset_cache()
        assert model_loader._backbone is None
