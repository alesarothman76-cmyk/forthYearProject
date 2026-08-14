import numpy as np
import pytest

from apps.mri_analysis.pipeline.convert import UnsupportedImageFormatError, convert
from apps.mri_analysis.pipeline.resize import resize
from apps.mri_analysis.pipeline.runner import run_preprocessing
from apps.mri_analysis.pipeline.skull_strip import skull_strip
from apps.mri_analysis.tests.helpers import make_synthetic_dicom_bytes, make_synthetic_png_bytes


class TestConvert:
    def test_raster_conversion_produces_rgb_array(self):
        png_bytes = make_synthetic_png_bytes()
        array, metadata = convert(png_bytes)
        assert array.ndim == 3
        assert array.shape[2] == 3
        assert metadata == {"original_format": "PNG"}

    def test_dicom_detected_and_converted(self):
        dicom_bytes = make_synthetic_dicom_bytes()
        array, metadata = convert(dicom_bytes)
        assert array.ndim == 3
        assert array.shape[2] == 3
        assert metadata["Modality"] == "MR"
        assert metadata["Manufacturer"] == "SyntheticTestVendor"

    def test_dicom_metadata_excludes_patient_identity_fields(self):
        dicom_bytes = make_synthetic_dicom_bytes()
        _, metadata = convert(dicom_bytes)
        assert "PatientName" not in metadata
        assert "PatientID" not in metadata
        assert "PatientBirthDate" not in metadata

    def test_dicom_pixel_spacing_is_list_of_strings(self):
        dicom_bytes = make_synthetic_dicom_bytes()
        _, metadata = convert(dicom_bytes)
        assert metadata["PixelSpacing"] == ["1.0", "1.0"]

    def test_garbage_input_raises_unsupported_format(self):
        with pytest.raises(UnsupportedImageFormatError):
            convert(b"not an image or dicom file")

    def test_empty_bytes_raises(self):
        with pytest.raises(UnsupportedImageFormatError):
            convert(b"")


class TestSkullStrip:
    def test_returns_same_shape(self):
        array, _ = convert(make_synthetic_png_bytes())
        stripped = skull_strip(array)
        assert stripped.shape == array.shape

    def test_degenerate_input_returns_original_unchanged(self):
        blank = np.zeros((64, 64, 3), dtype=np.uint8)
        result = skull_strip(blank)
        assert np.array_equal(result, blank)


class TestResize:
    def test_resizes_to_224(self):
        array = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        resized = resize(array)
        assert resized.shape == (224, 224, 3)


class TestRunner:
    def test_full_preprocessing_raster(self):
        result = run_preprocessing(make_synthetic_png_bytes())
        assert isinstance(result.processed_jpeg_bytes, bytes)
        assert isinstance(result.converted_jpeg_bytes, bytes)
        assert result.dicom_metadata is None

    def test_full_preprocessing_dicom_populates_metadata(self):
        result = run_preprocessing(make_synthetic_dicom_bytes())
        assert result.dicom_metadata is not None
        assert result.dicom_metadata["Modality"] == "MR"

    def test_garbage_input_propagates_error(self):
        with pytest.raises(UnsupportedImageFormatError):
            run_preprocessing(b"garbage")
