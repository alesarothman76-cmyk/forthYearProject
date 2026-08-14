# Alzheimer's MRI Diagnosis System

Django REST Framework backend implementing the system described in
`implementation_summary.md`. React frontend is out of scope for this
backend package (the spec treats it as a separate, lightly-specified
consumer of this API).

## What's implemented

- **Phase 1 — Accounts & Auth**: doctor self-registration, admin
  approve/reject workflow, JWT auth with role embedded in the token,
  password reset (also used for a doctor's first password), admin
  monitoring of doctor accounts.
- **Phase 2 — Patients**: doctor-owned patient records, soft-delete
  (archive), admin read-only non-clinical oversight (`medical_history`
  structurally excluded from the admin serializer).
- **Phase 3 + 4 — MRI Preprocessing + AI Analysis (merged)**: a single
  `POST /api/mri-scans/` endpoint runs the full pipeline synchronously:
  DICOM/raster auto-detect → convert → skull-strip → resize → classify
  (ResNet50 feature extractor → StandardScaler → SVM) → persist
  `AIAnalysisResult`. A failed pipeline never loses the `MRIScan` row —
  it's saved with `status=FAILED` and a clear `error_message`.
- **Phase 5 — Results/History**: `GET /api/patients/{id}/history/`
  aggregates a patient's full history in one call — every scan the owning
  doctor uploaded, each with its nested AI analysis result and the reports
  written against it.
- **Phase 6 — Reports**: doctor-authored reports against a scan's AI
  result. `DRAFT` reports are freely editable; `POST /reports/{id}/finalize/`
  generates a PDF snapshot (via **reportlab** — pure Python, no system
  deps) and transitions the report to `FINALIZED`, which is immutable
  (enforced in the service layer, not just the view) and permanent
  (can't be archived/deleted). `GET /reports/{id}/pdf/` downloads the
  generated PDF once finalized.

## Known current limitation (by design, not a bug)

The SVM (`svm_classifier.pkl`) and StandardScaler (`feature_scaler.pkl`)
artifacts are **not included** in this package (see Section 6.3/6.4/8.5 of
the spec — they were never re-provided). The ResNet50 backbone
(`resnet50_alzheimer.pth`) is also not included (large binary, gitignored
in the original project). Until all three files are placed under
`ml_models/` (paths configurable via `.env`), any real scan upload will
correctly complete preprocessing and then fail at the classification step
with a clear `error_message` — never a silent success, never an
unhandled 500. This exact behavior is covered by
`apps/mri_analysis/tests/test_services.py::test_real_upload_today_fails_at_classification_with_clear_message`,
which intentionally does not mock anything.

Tests that need the real backbone are marked `@pytest.mark.requires_backbone`
and are **auto-skipped** if `ml_models/resnet50_alzheimer.pth` isn't present
(see `pytest_collection_modifyitems` in the root `conftest.py`).

## Setup

```bash
cp .env.example .env          # adjust values as needed
docker compose up -d db       # local Postgres, matches .env.example defaults
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # defaults to role=ADMIN
python manage.py runserver
```
 
Run tests:

```bash
pytest                # add --create-db after model changes
```

The DB user needs `CREATEDB` privilege (pytest-django creates/drops
`test_<DB_NAME>` automatically).

## Project layout

See `implementation_summary.md` (Sections 2–3) for the full architectural
rationale. Short version: modular Django apps under `apps/`, each with
`models.py` / `serializers.py` / `services.py` (all business logic) /
`views.py` (thin) / `urls.py` / `admin.py` / `tests/`. Split settings under
`config/settings/{base,dev,prod,test}.py`.

## Outstanding items (carried over from the spec, Section 11)

1. Provide the real `svm_classifier.pkl` and `feature_scaler.pkl` (and
   `resnet50_alzheimer.pth`) under `ml_models/` — no code changes needed
   once provided.
2. Grad-CAM heatmap generation — deliberately not built yet, per your
   instruction to hold off until after this round (Phase 5/6) and the
   move to async/Celery. `AIAnalysisResult.heatmap_image` is already
   present and nullable, ready to be populated once built.
3. **Async/Celery for the MRI pipeline** — deliberately not done yet, per
   your instruction to hold off. Currently synchronous
   (`apps/mri_analysis/services.py::upload_and_process_scan`); the
   pipeline steps themselves (`apps/mri_analysis/pipeline/`) are already
   factored as plain functions with no request/response coupling, so
   wrapping them in a Celery task later should be a small, contained change.
4. Use-case diagram cleanup — cosmetic, not blocking.
5. `national_id` uniqueness against archived patients — currently global/
   permanent; flagged as a possible future refinement.
6. PDF report content is currently text/tables only (patient info, scan
   info, AI result distribution, doctor's notes) — no heatmap image, since
   heatmap generation itself is still pending (item 2 above). Once built,
   embedding it into the PDF is a small addition to
   `apps/reports/pdf.py::generate_report_pdf`.
