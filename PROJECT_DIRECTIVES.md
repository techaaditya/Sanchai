# Sanchai (सञ्चै) — Core Project Directives & Team Alignment

This document outlines the locked technical decisions and constraints for **Sanchai (सञ्चै)**. **All team members must align with these directives throughout the entire development lifecycle.**

---

## 1. AI Model Architecture Standard

* **Designated Model:** `gemma4:31b-cloud` (served via Ollama Cloud API: `https://ollama.com`).
* **API Credentials:** The team lead will configure `OLLAMA_API_KEY` in `.env`.
* **Deployment Pattern:**
  * **Primary:** `gemma4:31b-cloud` for high-accuracy document vision OCR and grounded clinical assistant interactions.
  * **Local / Offline Fallback:** Local Ollama (`http://localhost:11434`) for local testing.
  * **Zero-Crash Resilience:** All ingestion endpoints fail gracefully without crashing when offline.

---

## 2. Ingestion Scope & Modalities (Voice Input Strictly De-Scoped)

* **Voice / Audio Input Status:** **DE-SCOPED FOR NOW.**
  * We will **NOT** build or attempt voice/audio input features in this release. Voice recording and audio transcription pipelines are deferred to future post-hackathon versions.
* **Active Intake Modalities:**
  1. **Vision OCR (Images):** Handwritten doctor prescriptions, clinic slips, and photographed lab tests processed via `gemma4:31b-cloud`.
  2. **Digital PDFs:** Digital lab reports, discharge summaries, and insurance bills extracted instantly with PyMuPDF (0-second latency, zero model calls).
  3. **Direct Clinical Text:** Fast paste and raw clinical transcript intake.

---

## 3. The 3-Tier Clinical Normalization Guardrail

To guarantee clinical safety and eliminate hallucinations:
1. **Tier 1 (Exact Match):** Direct hash-map lookup against 261 curated Nepali clinical concepts.
2. **Tier 2 (Orthography & Fuzzy Match):** Devanagari matra folding (`ि/ी`, `ु/ू`), nukta dropping, and RapidFuzz with strict absolute Levenshtein edit distance budgets (prevents false positives like `Azee` vs `mg`).
3. **Tier 3 (Constrained Candidate Selection):** Fallback candidate selection constrained to valid lexicon IDs.
4. **Clinical Safety Rules:**
   * **Directional Negation Detection:** *"ज्वरो छैन"* flags fever as negated.
   * **Brand-to-Generic Translation:** *Cetamol* $\rightarrow$ *Paracetamol*, *Taxim-O* $\rightarrow$ *Cefixime*, *Pantocid* $\rightarrow$ *Pantoprazole*.
   * **Approval-Before-Write:** No pipeline directly mutates patient health records without user confirmation.

---

## 4. Git & Code Quality Rules

* Write clean, idiomatic, typed code (Pydantic v2 + FastAPI backend, Next.js App Router frontend).
* Commit messages must be precise, professional, and concise.
* **Do NOT include AI co-authored trailers** (`Co-authored-by: ...`) in git commit messages.
* Keep internal planning docs and archives strictly local (`rebuild_docs/`, `archive/`, and `*.zip` in `.gitignore`).
