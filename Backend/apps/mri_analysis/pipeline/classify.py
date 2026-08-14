"""
Implements exactly the verified pipeline from Section 6.5:
backbone.avgpool hook -> features -> scaler.transform() ->
svm.predict_proba() -> argmax + full distribution.
"""
import io
from dataclasses import dataclass

import numpy as np
from PIL import Image

from apps.mri_analysis.pipeline import model_loader

# Confirmed via ImageFolder alphabetical sort in the training notebook,
# independently re-confirmed after the OASIS retrain. Do NOT reorder
# without re-verifying against whatever SVM .pkl is actually loaded.
CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD = np.array([0.229, 0.224, 0.225])


@dataclass
class ClassificationResult:
    predicted_class: str
    confidence_score: float
    class_probabilities: dict


def _extract_features(jpeg_bytes: bytes) -> np.ndarray:
    """
    Resize((224,224)) -> ToTensor() -> Normalize(ImageNet mean/std) ->
    ResNet50 backbone (frozen) -> avgpool forward hook -> 2048-d features.
    Preprocessing at inference time exactly matches training: PIL bilinear,
    no augmentation.
    """
    import torch

    backbone = model_loader.get_backbone()

    image = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
    image = image.resize((224, 224), resample=Image.BILINEAR)

    array = np.array(image).astype(np.float32) / 255.0  # ToTensor: [0,1] range
    array = (array - IMAGENET_MEAN) / IMAGENET_STD  # Normalize
    tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0).float()  # CHW, add batch dim

    features_holder = {}

    def hook(module, hook_input, hook_output):
        features_holder["features"] = hook_output.detach().flatten(1)

    handle = backbone.avgpool.register_forward_hook(hook)
    try:
        with torch.no_grad():
            backbone(tensor)
    finally:
        handle.remove()

    return features_holder["features"].numpy()


def classify(jpeg_bytes: bytes) -> ClassificationResult:
    features = _extract_features(jpeg_bytes)

    scaler = model_loader.get_scaler()
    scaled_features = scaler.transform(features)

    svm = model_loader.get_svm()
    probabilities = svm.predict_proba(scaled_features)[0]

    predicted_index = int(np.argmax(probabilities))
    class_probabilities = {CLASS_NAMES[i]: float(probabilities[i]) for i in range(len(CLASS_NAMES))}

    return ClassificationResult(
        predicted_class=CLASS_NAMES[predicted_index],
        confidence_score=float(probabilities[predicted_index]),
        class_probabilities=class_probabilities,
    )
