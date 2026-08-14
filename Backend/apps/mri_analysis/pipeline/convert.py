"""
Step 1 of the preprocessing pipeline: detect DICOM vs standard raster image
and convert to a normalized RGB numpy array + metadata dict.
"""
import io

import numpy as np
from PIL import Image

# Allowlisted DICOM tags - deliberately excludes PatientName/PatientID/
# PatientBirthDate. The system already has its own Patient model owning
# identity; duplicating it from DICOM headers would create a second,
# harder-to-govern copy of identifying data.
ALLOWLISTED_DICOM_TAGS = [
    "Modality",
    "StudyDate",
    "StudyTime",
    "Manufacturer",
    "ManufacturerModelName",
    "MagneticFieldStrength",
    "SliceThickness",
    "PixelSpacing",
    "Rows",
    "Columns",
    "BitsAllocated",
    "PhotometricInterpretation",
    "RepetitionTime",
    "EchoTime",
    "ProtocolName",
    "SeriesDescription",
]


class UnsupportedImageFormatError(Exception):
    """Raised for garbage/unreadable input. Caught by the service layer and
    turned into status=FAILED with a message - never an unhandled 500."""


def _is_dicom(raw_bytes: bytes) -> bool:
    """Detects DICOM via magic bytes ('DICM' at byte offset 128), not file extension."""
    return len(raw_bytes) > 132 and raw_bytes[128:132] == b"DICM"


def _extract_dicom_metadata(dataset) -> dict:
    metadata = {}
    for tag in ALLOWLISTED_DICOM_TAGS:
        if hasattr(dataset, tag):
            value = getattr(dataset, tag)
            # Multi-valued DICOM elements (e.g. PixelSpacing) cast to plain
            # lists of strings for JSON-serializability.
            if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
                metadata[tag] = [str(v) for v in value]
            else:
                metadata[tag] = str(value)
    return metadata


def _convert_dicom(raw_bytes: bytes):
    import pydicom
    from pydicom.pixel_data_handlers.util import apply_voi_lut

    try:
        dataset = pydicom.dcmread(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise UnsupportedImageFormatError(f"Could not parse DICOM file: {exc}") from exc

    try:
        pixel_array = dataset.pixel_array
    except Exception as exc:
        raise UnsupportedImageFormatError(f"Could not read DICOM pixel data: {exc}") from exc

    # Apply VOI LUT/windowing so pixel intensities render the way a
    # radiologist's viewer would.
    windowed = apply_voi_lut(pixel_array, dataset)

    # Normalize to 8-bit.
    windowed = windowed.astype(np.float64)
    min_val, max_val = windowed.min(), windowed.max()
    if max_val > min_val:
        normalized = (windowed - min_val) / (max_val - min_val) * 255.0
    else:
        normalized = np.zeros_like(windowed)
    image_8bit = normalized.astype(np.uint8)

    # Replicate grayscale to 3 channels (model expects RGB).
    if image_8bit.ndim == 2:
        rgb_array = np.stack([image_8bit] * 3, axis=-1)
    else:
        rgb_array = image_8bit

    metadata = _extract_dicom_metadata(dataset)
    return rgb_array, metadata


def _convert_raster(raw_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(raw_bytes))
        image.load()
    except Exception as exc:
        raise UnsupportedImageFormatError(f"Could not open image: {exc}") from exc

    original_format = image.format or "UNKNOWN"
    rgb_image = image.convert("RGB")
    rgb_array = np.array(rgb_image)

    metadata = {"original_format": original_format}
    return rgb_array, metadata


def convert(raw_bytes: bytes):
    """
    Auto-detects DICOM vs standard raster (PNG/TIFF/BMP/JPEG/etc.) and
    returns (rgb_array, metadata_dict). Format-agnostic since whether
    uploads are raw DICOM or already-extracted 2D slices was never fully
    resolved (Section 7.1 item 5).
    """
    if not raw_bytes:
        raise UnsupportedImageFormatError("Empty file.")

    if _is_dicom(raw_bytes):
        return _convert_dicom(raw_bytes)
    return _convert_raster(raw_bytes)
