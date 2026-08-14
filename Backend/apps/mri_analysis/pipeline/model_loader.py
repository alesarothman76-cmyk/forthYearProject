"""
Lazy singleton loaders for the ResNet50 backbone, StandardScaler, and SVM.

Each is loaded once on first actual use (not at Django startup/import
time), and cached process-wide. This means importing the app or running
migrations never fails just because weight files aren't deployed yet in a
given environment - only an actual classification attempt does, with a
clear, actionable error message naming the missing file.
"""
import threading

_backbone = None
_scaler = None
_svm = None
_lock = threading.Lock()


class ModelArtifactMissingError(Exception):
    """Raised with a clear, actionable message naming the missing file."""


def _resnet_backbone_path():
    from django.conf import settings

    return settings.RESNET_BACKBONE_PATH

 
def _svm_path():
    from django.conf import settings

    return settings.SVM_CLASSIFIER_PATH


def _scaler_path():
    from django.conf import settings

    return settings.FEATURE_SCALER_PATH


def get_backbone():
    """
    Loads the ResNet50 backbone (frozen feature extractor).
    Confirmed via direct torch.load() + strict=True into
    torchvision.models.resnet50(weights=None) with model.fc replaced by
    nn.Linear(2048, 4). It's a raw state_dict, not a full checkpoint.
    """
    global _backbone
    if _backbone is not None:
        return _backbone

    with _lock:
        if _backbone is not None:
            return _backbone

        path = _resnet_backbone_path()
        if not path.exists():
            raise ModelArtifactMissingError(
                f"ResNet50 backbone weights not found at '{path}'. "
                "Place the file there or set RESNET_BACKBONE_PATH."
            )

        import torch
        import torch.nn as nn
        import torchvision.models as models

        backbone = models.resnet50(weights=None)
        backbone.fc = nn.Linear(2048, 4)
        state_dict = torch.load(path, map_location="cpu")
        backbone.load_state_dict(state_dict, strict=True)
        backbone.eval()

        _backbone = backbone
        return _backbone


def get_scaler():
    """
    Required between backbone and SVM - support vector statistics prove the
    SVM was fit on scaled features (see Section 6.3/6.4 of the
    implementation summary). Must be the exact scaler fit during the OASIS
    SVM retrain.
    """
    global _scaler
    if _scaler is not None:
        return _scaler

    with _lock:
        if _scaler is not None:
            return _scaler

        import joblib

        path = _scaler_path()
        if not path.exists():
            raise ModelArtifactMissingError(
                f"StandardScaler artifact not found at '{path}'. "
                "This file has never been uploaded to the project - see "
                "Section 6.4/Section 11 item 1 of the implementation summary. "
                "Place it there or set FEATURE_SCALER_PATH."
            )

        _scaler = joblib.load(path)  # NOT raw pickle.load() - raw pickle fails on this file.
        return _scaler


def get_svm():
    global _svm
    if _svm is not None:
        return _svm

    with _lock:
        if _svm is not None:
            return _svm

        import joblib

        path = _svm_path()
        if not path.exists():
            raise ModelArtifactMissingError(
                f"SVM classifier artifact not found at '{path}'. "
                "Place it there or set SVM_CLASSIFIER_PATH."
            )

        _svm = joblib.load(path)  # NOT raw pickle.load() - raw pickle fails on this file.
        return _svm


def reset_cache():
    """Test-only helper to clear the process-wide singleton cache between tests."""
    global _backbone, _scaler, _svm
    _backbone = None
    _scaler = None
    _svm = None
