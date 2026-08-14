import numpy as np
import pytest

from apps.mri_analysis.pipeline import model_loader


class _FakeScaler:
    def transform(self, features):
        return features  # no-op scaling for deterministic test behavior


class _FakeSVM:
    """Deterministic fake: always predicts NonDemented with fixed confidence."""

    def predict_proba(self, features):
        # [MildDemented, ModerateDemented, NonDemented, VeryMildDemented]
        return np.array([[0.05, 0.05, 0.80, 0.10]])


@pytest.fixture
def mock_classifier(monkeypatch):
    """
    Stubs out only the scaler/SVM with deterministic fakes - the real
    backbone weights are still used for feature extraction. This proves
    the wiring is correct; it explicitly does NOT validate real
    classification accuracy, which requires the actual trained artifacts.
    """
    model_loader.reset_cache()
    monkeypatch.setattr(model_loader, "get_scaler", lambda: _FakeScaler())
    monkeypatch.setattr(model_loader, "get_svm", lambda: _FakeSVM())
    yield
    model_loader.reset_cache()
