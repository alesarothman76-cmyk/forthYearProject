"""
Synthetic DICOM/PNG fixtures for tests. Built procedurally in-memory - never
real clinical data.
"""
import io

import numpy as np
from PIL import Image


def make_synthetic_png_bytes(size=(256, 256)) -> bytes:
    """A simple synthetic grayscale-ish 'brain-like' raster image."""
    rng = np.random.default_rng(42)
    array = rng.integers(low=20, high=200, size=(*size, 3), dtype=np.uint8)
    # Draw a bright circular blob in the middle to mimic a head silhouette.
    yy, xx = np.ogrid[: size[0], : size[1]]
    center = (size[0] // 2, size[1] // 2)
    radius = min(size) // 3
    mask = (xx - center[1]) ** 2 + (yy - center[0]) ** 2 <= radius**2
    array[mask] = [180, 180, 180]

    image = Image.fromarray(array, mode="RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_synthetic_dicom_bytes(size=(256, 256)) -> bytes:
    """Procedurally builds a minimal valid DICOM file using pydicom.dataset.FileDataset."""
    import pydicom
    from pydicom.dataset import FileDataset, FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian, generate_uid

    rng = np.random.default_rng(7)
    pixel_array = rng.integers(low=0, high=4096, size=size, dtype=np.uint16)

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = generate_uid()
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    buffer = io.BytesIO()
    dataset = FileDataset(buffer, {}, file_meta=file_meta, preamble=b"\x00" * 128)

    dataset.Modality = "MR"
    dataset.StudyDate = "20240101"
    dataset.StudyTime = "120000"
    dataset.Manufacturer = "SyntheticTestVendor"
    dataset.ManufacturerModelName = "SyntheticScanner3000"
    dataset.MagneticFieldStrength = "3.0"
    dataset.SliceThickness = "1.0"
    dataset.PixelSpacing = ["1.0", "1.0"]
    dataset.Rows, dataset.Columns = size
    dataset.BitsAllocated = 16
    dataset.BitsStored = 12
    dataset.HighBit = 11
    dataset.PixelRepresentation = 0
    dataset.PhotometricInterpretation = "MONOCHROME2"
    dataset.RepetitionTime = "500"
    dataset.EchoTime = "20"
    dataset.ProtocolName = "SyntheticT1"
    dataset.SeriesDescription = "Synthetic test series"
    dataset.SamplesPerPixel = 1

    # Fields the test dataset should NOT include per the allowlist, but
    # setting them anyway proves convert.py correctly excludes them.
    dataset.PatientName = "Test^Synthetic"
    dataset.PatientID = "SYN-000"
    dataset.PatientBirthDate = "19700101"

    dataset.PixelData = pixel_array.tobytes()
    dataset.is_little_endian = True
    dataset.is_implicit_VR = False

    dataset.save_as(buffer, enforce_file_format=True)
    return buffer.getvalue()
