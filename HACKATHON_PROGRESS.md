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
- **Commit:** (Pending)
- **Next Task:** Increment 3: Document intake and 3-tier normalization integration (`backend/routers/intake.py` and document extraction for PDF, images, and text).
