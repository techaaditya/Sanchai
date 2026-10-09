# Sanchai (सञ्चै) — Hackathon Progress Log

## Workstream: Person B (Backend Lead)
**Active Branch:** `shubham`  
**Base:** `origin/main` (commit `bc9ecf8`)

---

### Increment 1: Backend Startup & Health Endpoint
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Initialized FastAPI core application in `backend/main.py`.
  - Configured CORS middleware reading `settings.cors_origin_list`.
  - Implemented `/api/v1/health` with offline-resilient service probing (SQLite DB status and Ollama cloud/local model endpoint).
  - Added `pyproject.toml` pytest configuration.
  - Added unit test in `tests/test_health.py`.
- **Verification:**
  - `pytest tests/test_health.py`: 1 passed in 1.56s.
  - Health endpoint returns `{"status": "ok", "service": "sanchai-api", ...}`.
- **Commit:** `8c7b91f`
- **Next Task:** Increment 2: SQLite database foundation and synthetic seed data loader (`backend/db.py` & `backend/seed.py`).

---

### Increment 2: SQLite Foundation & Synthetic Seed Data
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Implemented SQLite database layer in `backend/db.py` with `patients`, `allergies`, `record_entries`, `lexicon_entries`, and `eval_results` schemas, transaction session context manager, and additive migration support.
  - Implemented data seeding in `backend/seed.py` loading `data/nepali_clinical_lexicon.json`, `data/seed_patients.json`, and `data/seed_entries.json` with deterministic QR tokens and Sanchai IDs.
  - Integrated lifespan startup hook in `backend/main.py` ensuring automated database init and idempotent seeding.
  - Added integration tests in `tests/test_db_seed.py`.
- **Verification:**
  - `pytest tests/test_db_seed.py tests/test_health.py`: 4 passed in 9.10s.
  - Health probe confirms database status is "up".
- **Commit:** `c9862df`
- **Next Task:** Increment 3: Document intake and 3-tier normalization integration (`backend/routers/intake.py` and document extraction for PDF, images, and text).

---

### Increment 3: Document Intake & 3-Tier Normalization Integration
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Implemented `backend/intake/documents.py` for instant PyMuPDF digital PDF text extraction, rasterization for scanned docs, and rule-based document classification.
  - Implemented `backend/intake/storage.py` for content-addressed asset storage preventing path traversal.
  - Implemented `backend/intake/pipeline.py` orchestrating routing -> extraction -> spell-correction -> classification -> 3-tier normalization -> SSE event progression.
  - Implemented `backend/routers/intake.py` with `/api/v1/intake/text`, `/api/v1/intake/ocr`, `/api/v1/intake/stream` (SSE), and `/api/v1/intake/normalize`.
  - Added comprehensive test coverage in `tests/test_intake.py`.
- **Verification:**
  - `pytest tests/test_intake.py`: 5 passed in 0.62s.
  - Full suite (`pytest`): 9 passed in 2.50s.
  - Digital PDF extraction verified via in-memory PyMuPDF documents.
  - Offline vision OCR resilience verified against uncontactable model backends.
- **Commit:** `4dd650b`
- **Next Task:** Increment 4: Explicit approval-before-write gate and patient record entry commit (`backend/record/entries.py` and `POST /api/v1/patients/{id}/entries`).

---

### Increment 4: Approval-Before-Write Gate & Patient Record Retrieval
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Implemented `backend/record/entries.py` with concept hydration against active lexicon, normalization encoding, timeline summaries with negation badges (`✕`), and active conditions extraction excluding negated findings.
  - Implemented `backend/routers/patients.py` with `GET /api/v1/patients`, `GET /api/v1/patients/{id}`, `GET /api/v1/patients/{id}/record`, `GET /api/v1/patients/{id}/entries/{entry_id}`.
  - Implemented `POST /api/v1/patients/{id}/entries`: the **Approval-Before-Write gate** — the only route permitted to mutate `record_entries` in SQLite, requiring verified Gregorian dates and explicit user commitment.
  - Mounted patients router into `backend/main.py`.
  - Added comprehensive test suite in `tests/test_patients_and_approval.py`.
- **Verification:**
  - `pytest tests/test_patients_and_approval.py`: 5 passed in 0.60s.
  - Full test suite (`pytest`): 14 passed in 3.44s.
  - Verified approval gate commit increases patient timeline by 1 and prevents uncommitted mutations.
- **Commit:** `2de4fc4`
- **Next Task:** Increment 5: QR generation and emergency payload encoding (`backend/record/qr.py` and `GET /api/v1/patients/{id}/qr`).

---

### Increment 5: Segno QR Generation & Emergency Payload
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Implemented `backend/record/qr.py` utilizing `segno` (with `qrcode` fallback) to generate high-contrast scannable QR codes for emergency responders.
  - Built `build_qr_payload` constructing `QrPayload` with `sanchai_id`, `qr_token`, `encodes`, allergies, active conditions, and base64 PNG data URI.
  - Added `GET /api/v1/patients/{id}/qr` (JSON and PNG format) and `GET /api/v1/patients/{id}/qr.png` (direct image streaming).
  - Added unit test suite in `tests/test_qr.py`.
- **Verification:**
  - `pytest tests/test_qr.py`: 4 passed in 0.64s.
  - Full test suite (`pytest`): 18 passed in 4.17s.
  - Verified genuine PNG bytes generation with `\x89PNG\r\n\x1a\n` header.
- **Commit:** `a899370`
- **Next Task:** Increment 6: FHIR R4 interoperability bundle export strictly excluding negated findings (`backend/record/fhir.py` and `GET /api/v1/patients/{id}/fhir`).

---

### Increment 6: FHIR R4 Export with Strict Negation Exclusion
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Implemented `backend/record/fhir.py` generating HL7 FHIR R4 collection bundles with `Patient`, `AllergyIntolerance`, `Condition`, `MedicationRequest`, and `Observation` resources.
  - Enforced critical clinical safety rule: strictly excluded negated findings from `Condition` resources to prevent inverting clinical records in external health systems.
  - Tracked `negated_excluded` count on bundle payload for transparent clinical auditing.
  - Implemented `GET /api/v1/patients/{id}/fhir` endpoint returning valid `FhirBundle`.
  - Added unit and safety tests in `tests/test_fhir.py`.
- **Verification:**
  - `pytest tests/test_fhir.py`: 3 passed in 0.56s.
  - Full test suite (`pytest`): 21 passed in 2.14s.
  - Verified `negated_excluded >= 1` and confirmed no negated conditions appear in exported resources.
- **Commit:** `d233965`
- **Next Task:** Increment 7: Comprehensive end-to-end integration tests (`tests/test_integration_flow.py`).

---

### Increment 7: End-to-End Clinical Flow Integration Tests
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Implemented `tests/test_integration_flow.py` asserting the complete clinician lifecycle:
    1. System health probe `/api/v1/health` verification
    2. Patient retrieval `/api/v1/patients`
    3. Multimodal document intake simulation with instant PyMuPDF PDF extraction and 3-tier normalization
    4. Guardrail validation: verifying uncommitted intake produces 0 database mutations
    5. Approval-Before-Write gate execution via `POST /api/v1/patients/{id}/entries`
    6. Timeline chronology verification and entry retrieval
    7. Emergency Segno QR validation (JSON payload and PNG binary stream)
    8. Interoperable HL7 FHIR R4 export validation with strict negation exclusion
- **Verification:**
  - `pytest tests/test_integration_flow.py`: 1 passed in 1.90s.
  - Full project test suite (`pytest`): 22 passed in 2.70s.
- **Commit:** `04f2c53`
- **Next Task:** Maintain demo readiness and coordinate API contracts with Person 1 (Frontend) and Person 3 (AI Model Serving).

---

### Increment 8: Per-Test Database Isolation
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Added `tests/conftest.py` with an autouse fixture overriding `settings.db_path` and `settings.upload_dir` to a per-test `tmp_path`, so `TestClient(app)` lifespan re-seeds an isolated database instead of mutating `data/sanchai.db`.
  - Confirmed the development database had been polluted by earlier runs (duplicate seeded rows) and was cleaned and re-seeded.
- **Verification:**
  - Full test suite (`pytest`): 24 passed in 4.67s (verified across reruns; dev DB row counts stable).
- **Commit:** `7f55dde`
- **Next Task:** Increment 9: FHIR R4 resource compliance.

---

### Increment 9: FHIR R4 Spec Compliance and Model Validation
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Rewrote `backend/record/fhir.py`: FHIR-safe resource IDs (underscores replaced with hyphens, matching R4 pattern `^[A-Za-z0-9\-.]+$`; internal IDs such as `patient_ram` remain unchanged elsewhere), `Condition.cclinicalStatus` set to `active`, `MedicationRequest` uses CodeableReference `medication: {concept: ...}`, Observation status `final`.
  - Added `validate_bundle()` using the already-installed `fhir.resources.Bundle` model; `build_bundle()` now validates before returning.
- **Verification:**
  - `pytest tests/test_fhir.py`: 5 passed.
  - Full test suite (`pytest`): 24 passed in 4.67s.
- **Commit:** `a42ed0f`
- **Next Task:** Increment 10: hardening pass (SSE, upload limits, validation).

---

### Increment 10: SSE Error Propagation and Generator Cleanup
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Confirmed defect: a mid-stream pipeline failure (e.g. `save_upload` storage error, which runs *after* the stream opens) escaped the SSE generator and silently truncated the response with no terminal event; upstream generator closure relied only on CPython refcounting.
  - `_sse` now catches pipeline exceptions, emits a terminal `event: error` frame with failure detail (streaming headers are already sent, so the status cannot change), and always closes the upstream `run_intake` generator in `finally` — including on client disconnect (`GeneratorExit`).
- **Verification:**
  - `pytest tests/test_intake.py`: 8 passed.
  - Full test suite (`pytest`): 27 passed in 4.38s.
- **Commit:** `5c7968a`
- **Next Task:** Increment 11: corrupted-PDF status accuracy.

---

### Increment 11: Accurate Failure Status for Corrupted PDFs
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Confirmed defect: garbage/corrupted PDF bytes raised `FileDataError` in `extract_pdf_text`, was caught by a broad handler that set `extraction_status='engine_unavailable'` — falsely claiming the AI model backend was unreachable (it was never contacted) — while `extraction_method` stayed `'direct'` as if text had been extracted.
  - Parse and rasterization failures now report `extraction_status='unsupported'` (a documented value previously never emitted) and `extraction_method='unavailable'`; OCR-model-unreachable keeps `engine_unavailable`.
- **Verification:**
  - `pytest tests/test_intake.py`: 9 passed (new `test_intake_malformed_pdf_reports_unsupported`).
  - Full test suite (`pytest`): 28 passed in 3.99s.
- **Commit:** `e23bc01`
- **Next Task:** Increment 12: upload size limits.

---

### Increment 12: Bounded Upload Size Enforcement
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Confirmed defect: `_read_upload` called `file.read()` on the whole upload before checking size, materialising arbitrarily large bodies in RAM before the 413 check.
  - Now rejects on parsed `UploadFile.size` first (no bytes read) and falls back to a bounded 1 MB chunked read that aborts once the limit is crossed; empty uploads still return 422.
  - Added an ASGI-level `Content-Length` gate in `backend/main.py` (25 MB + 1 MB multipart slack) rejecting oversized bodies *before* the multipart parser buffers them; registered before `CORSMiddleware` so CORS stays outermost and 413 responses still carry CORS headers (pinned by test).
- **Verification:**
  - `pytest tests/test_intake.py`: 12 passed (new 413, 422, and Content-Length-gate-with-CORS tests).
  - Full test suite (`pytest`): 31 passed in 4.66s (streaming and all other endpoints unaffected by the middleware).
- **Commit:** `b765cd1`
- **Next Task:** Increment 13: approval-gate input validation.

---

### Increment 13: Input Validation at the Approval-Before-Write Gate
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Confirmed defect: `POST /api/v1/patients/{id}/entries` — the only route that mutates the authoritative record — accepted arbitrary `input_type` and `document_class` strings, although the schema documents `input_type` as `text | image | pdf` and intake validates `document_class` against the four documented classes. Undocumented values would be committed where `document_class` filters silently miss them.
  - The gate now rejects invalid `input_type` (voice remains de-scoped per PROJECT_DIRECTIVES) and unknown `document_class` with 422 *before* touching the database; regression test asserts rejected requests leave the record unchanged while documented values still commit.
  - Also closed a related gap: `/intake/stream` accepted unbounded `Form` text while `/intake/text` caps at 20,000 chars via schema — the streaming route now enforces the same 20,000-char cap before opening the stream.
- **Verification:**
  - `pytest tests/test_patients_and_approval.py`: 6 passed.
  - `pytest tests/test_intake.py`: 13 passed (new oversized-text test).
  - Full test suite (`pytest`): 32 then 37 passed.
- **Commits:** `f702343`, `cc3638c`
- **Next Task:** Increment 14: FHIR/QR privacy regression tests.

---

### Increment 14: FHIR Negative Validation and QR Privacy Boundary Tests
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - FHIR review findings: existing tests proved the bundle *passes* `fhir.resources` validation but never proved the validator *rejects* invalid input; patient-reference checks were genuine (references compared against the actual Patient resource id in the bundle).
  - Added `test_validate_bundle_rejects_invalid_resources` — `validate_bundle` must raise on an underscore resource id and on a Condition missing required `clinicalStatus`, proving the validator is not vacuously passing.
  - Added `test_fhir_patient_references_point_to_bundle_resources` — every `Patient/...` reference must be well-formed and resolve to the Patient resource present in the bundle (no dangling references).
  - QR review findings: no endpoint resolves `qr_token` (no token-based lookup = no enumeration surface); emergency payload contains only name, blood group, allergies, and non-negated conditions — no internal row id, dob, district, or entries; QR image encodes only the opaque `sanchai://p/{token}` reference.
  - Added `test_qr_payload_only_exposes_emergency_fields` and `test_qr_conditions_exclude_negated_findings` (negated ज्वरो छैन never appears as an active condition) to pin this boundary.
- **Verification:**
  - `pytest tests/test_fhir.py tests/test_qr.py`: 13 passed.
  - Full test suite (`pytest`): 36 then 37 passed.
- **Commit:** `7fb0383`
- **Next Task:** Final verification and this log update.

---

### Increment 15: Progress Log Update (Verified Hardening Pass)
- **Status:** COMPLETED & VERIFIED
- **Changes:**
  - Recorded verified results for Increments 8–14 with actual commit hashes and measured test counts.
- **Known limitations (documented, intentionally not changed without team agreement):**
  - QR tokens are deterministic (sha256[:16] of `sanchai:` + id) for cross-device demo consistency — not a bearer secret; since no endpoint accepts `qr_token` as a credential, it grants no access today. A future token-resolver endpoint must switch to random, unguessable tokens.
  - No authentication/authorization on any endpoint (matches current frontend contract; adding auth is an architecture decision requiring team agreement). The approval gate is validated but not authenticated.
  - `extraction_status`/`input_type` failures return 422/413 pre-stream; unexpected mid-stream failures return `event: error` (HTTP status cannot change after streaming starts).
- **Verification:**
  - Full test suite (`pytest`): 37 passed, 6 warnings (~5–6s).
- **Commit:** (this commit)
- **Next Task:** Coordinate with Person 1 (Frontend) on SSE `error` event handling and with Person 3 (AI Model Serving) on vision-model OCR availability.
