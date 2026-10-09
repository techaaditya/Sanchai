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
- **Commit:** (Pending)
- **Next Task:** Increment 7: Comprehensive end-to-end integration tests (`tests/test_integration_flow.py`).
