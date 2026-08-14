import time

from django.core.files.base import ContentFile
from django.db import transaction

from apps.mri_analysis.models import AIAnalysisResult, MRIScan, ScanStatus
from apps.mri_analysis.pipeline.classify import classify
from apps.mri_analysis.pipeline.convert import UnsupportedImageFormatError
from apps.mri_analysis.pipeline.model_loader import ModelArtifactMissingError
from apps.mri_analysis.pipeline.runner import run_preprocessing


def upload_and_process_scan(*, doctor, patient, uploaded_file):
    """
    Merged entry point (Phase 3 + 4). Runs the full pipeline
    (preprocessing then classification) synchronously. The MRIScan row is
    always created and persisted first, regardless of what happens next, so
    an upload is never lost. Sets COMPLETED or FAILED with a clear message
    on any exception - never a silent failure or an unhandled 500.
    """
    raw_bytes = uploaded_file.read()

    scan = MRIScan.objects.create(
        patient=patient,
        uploaded_by_doctor=doctor,
        original_file=ContentFile(raw_bytes, name=uploaded_file.name),
        status=ScanStatus.PENDING,
    )

    _run_pipeline(scan=scan, raw_bytes=raw_bytes)
    return scan


def reprocess_scan(*, scan):
    """Re-runs the pipeline against the already-stored original_file, without requiring a new upload."""
    scan.original_file.open("rb")
    try:
        raw_bytes = scan.original_file.read()
    finally:
        scan.original_file.close()

    _run_pipeline(scan=scan, raw_bytes=raw_bytes)
    return scan


def _run_pipeline(*, scan: MRIScan, raw_bytes: bytes):
    scan.status = ScanStatus.PROCESSING
    scan.error_message = ""
    scan.save(update_fields=["status", "error_message", "updated_at"])

    start_time = time.monotonic()
    try:
        preprocess_result = run_preprocessing(raw_bytes)

        scan.processed_image.save(
            f"scan_{scan.id}_processed.jpg",
            ContentFile(preprocess_result.processed_jpeg_bytes),
            save=False,
        )
        scan.dicom_metadata = preprocess_result.dicom_metadata

        classification = classify(preprocess_result.processed_jpeg_bytes)
        execution_time = time.monotonic() - start_time

        with transaction.atomic():
            scan.status = ScanStatus.COMPLETED
            scan.save()
            AIAnalysisResult.objects.update_or_create(
                mri_scan=scan,
                defaults={
                    "predicted_class": classification.predicted_class,
                    "confidence_score": classification.confidence_score,
                    "class_probabilities": classification.class_probabilities,
                    "execution_time_seconds": execution_time,
                },
            )
    except (UnsupportedImageFormatError, ModelArtifactMissingError) as exc:
        scan.status = ScanStatus.FAILED
        scan.error_message = str(exc)
        scan.save(update_fields=["status", "error_message", "dicom_metadata", "updated_at"])
    except Exception as exc:  # noqa: BLE001 - deliberately broad: never a silent 500
        scan.status = ScanStatus.FAILED
        scan.error_message = f"Unexpected error during processing: {exc}"
        scan.save(update_fields=["status", "error_message", "dicom_metadata", "updated_at"])
