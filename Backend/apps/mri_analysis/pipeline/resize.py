"""
Step 3 of the preprocessing pipeline: resize to model input size.

PIL bilinear resize to 224x224, not OpenCV - deliberately matching the
training pipeline's transforms.Resize (which uses PIL under the hood) to
avoid a subtle train/inference distribution shift from a
differently-implemented "equivalent" resize.
"""
import numpy as np
from PIL import Image

TARGET_SIZE = (224, 224)


def resize(rgb_array: np.ndarray) -> np.ndarray:
    image = Image.fromarray(rgb_array.astype(np.uint8), mode="RGB")
    resized_image = image.resize(TARGET_SIZE, resample=Image.BILINEAR)
    return np.array(resized_image)
