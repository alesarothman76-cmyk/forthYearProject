"""
Orchestrates convert -> skull_strip -> resize in order, producing the final
processed JPEG bytes (what Phase 4's classification step consumes) plus the
original format-converted (but NOT stripped/resized) JPEG, kept for
audit/reference.
"""
import io
from dataclasses import dataclass

import numpy as np
from PIL import Image

from apps.mri_analysis.pipeline.convert import convert
from apps.mri_analysis.pipeline.resize import resize
from apps.mri_analysis.pipeline.skull_strip import skull_strip


@dataclass
class PreprocessResult:
    processed_jpeg_bytes: bytes
    converted_jpeg_bytes: bytes
    dicom_metadata: dict | None


def _to_jpeg_bytes(rgb_array: np.ndarray) -> bytes:
    image = Image.fromarray(rgb_array.astype(np.uint8), mode="RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def run_preprocessing(raw_bytes: bytes) -> PreprocessResult:
    rgb_array, metadata = convert(raw_bytes)
    converted_jpeg_bytes = _to_jpeg_bytes(rgb_array)

    stripped_array = skull_strip(rgb_array)
    resized_array = resize(stripped_array)
    processed_jpeg_bytes = _to_jpeg_bytes(resized_array)

    # dicom_metadata populated only for DICOM sources (raster sources have
    # only {"original_format": ...}, which we don't store as dicom_metadata).
    dicom_metadata = metadata if "Modality" in metadata else None

    return PreprocessResult(
        processed_jpeg_bytes=processed_jpeg_bytes,
        converted_jpeg_bytes=converted_jpeg_bytes,
        dicom_metadata=dicom_metadata,
    )
