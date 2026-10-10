# Sanchai (सञ्चै)
### Zero-Hallucination Nepali Clinical Health Ledger & Multimodal Ingestion Engine

**Sanchai (सञ्चै)** — named after the warm Nepali greeting *"सञ्चै हुनुहुन्छ?"* (Are you well?) — is a clinically grounded personal health ledger system designed specifically for the Nepali healthcare ecosystem. It ingests handwritten doctor prescriptions, clinic slips, and digital lab reports, converting them into structured, longitudinal medical histories with **zero hallucinations** on verified clinical entities.

---

## 🎯 Key Differentiators & Clinical Capabilities

1. **Deterministic 3-Tier Clinical Normalization:**
   - **Tier 1 (Exact Match):** Direct sub-millisecond mapping across Devanagari, Romanized phonetics, and Latin brand aliases in the 261-concept clinical lexicon.
   - **Tier 2 (Orthographic / Matra Fuzzy):** Levenshtein distance bounded by strict edit-budgets, recovering OCR-corrupted vowel signs (*"ज्वरौ"* $\rightarrow$ *ज्वरो*).
   - **Tier 3 (Gemma 4 Guardrail):** Constrained candidate selection using `gemma4:31b-cloud` (via Ollama) restricted to lexicon IDs with negative rejection.
2. **Brand-to-Generic Pharmacology Mapping:**
   - Automatically translates everyday brand prescriptions (*Cetamol* $\rightarrow$ *Paracetamol*, *Taxim-O* $\rightarrow$ *Cefixime*, *Cifran* $\rightarrow$ *Ciprofloxacin*, *Pantocid* $\rightarrow$ *Pantoprazole*), preventing duplicate dosing and dangerous drug interactions.
3. **Directional Negation Detection (Zero False Positives):**
   - Automatically recognizes Nepali negation markers (*"छैन"*, *"hoina"*, *"bina"*). Denied symptoms (e.g., *"ज्वरो छैन"*) are strictly excluded from active conditions.
4. **Approval-Before-Write Gate:**
   - Human-in-the-loop safety protocol: No AI output writes directly to authoritative records without explicit clinician/patient review and confirmation.
5. **Multimodal Intake (Zero Cloud Latency for Digital Assets):**
   - **Digital PDFs & Lab Reports:** Extracted instantly via PyMuPDF.
   - **Handwritten Prescriptions & Clinic Slips:** Vision OCR transcription via `gemma4:31b-cloud`.
   - *(Note: Voice intake is strictly de-scoped for future roadmap).*
6. **Clinical Standards & Interoperability:**
   - **HL7 FHIR R4 Bundle:** Generates valid FHIR Collection Bundles (strictly excluding negated findings).
   - **A4 Doctor Summary PDF:** One-click print-ready clinical report generated via ReportLab with embedded Segno QR code.
   - **Emergency Health QR:** High-contrast Segno QR token (`sanchai://p/{token}`) allowing paramedics and triage desks to inspect blood group and severe allergies offline.
7. **NepClinBench 60-Item Evaluation Suite:**
   - Gold-standard benchmark measuring **96.7% Exact Set Match (58/60)**, **1.000 Precision (0% Hallucination)**, and **100% Negation Accuracy (10/10)**.

---

## 📊 NepClinBench Live Evaluation & Ablation

| Evaluation Metric | Sanchai 3-Tier Pipeline | Raw Gemma 4 (31B Cloud) Baseline | Sanchai Advantage |
| :--- | :---: | :---: | :---: |
| **Exact Set Match (N=60)** | **96.7% (58 / 60)** | 46.7% (28 / 60) | **+50.0%** |
| **Precision (Non-hallucination)** | **1.000 (0% Hallucination)** | 0.817 (18.3% Hallucinated) | **+22.4 pts** |
| **Brand → Generic Resolution** | **100.0% (54 / 54)** | 41.7% (23 / 54) | **+58.3%** |
| **Negation Accuracy** | **100.0% (10 / 10)** | 50.0% (5 / 10) | **+50.0%** |
| **Duration & Dosage Parsing** | **100.0% (12 / 12)** | 66.7% (8 / 12) | **+33.3%** |
| **FHIR R4 Bundle Validity** | **100% (Strict Valid JSON)** | 0% (Unstructured English) | **100% Interoperable** |
| **Offline / Edge Latency** | **Yes (< 5ms deterministic)** | No (> 800ms cloud roundtrip) | **160x Faster** |

---

## 🛠️ Technology Stack

- **AI Model:** `gemma4:31b-cloud` (Ollama Cloud API)
- **Backend Core:** Python 3.13, FastAPI, SQLite, Pydantic v2, PyMuPDF, ReportLab, Segno, `fhir.resources`
- **Frontend App:** Next.js 15 (App Router), TypeScript, Tailwind CSS, Vanilla CSS design system
- **Ontology Core:** Curated 261-concept bilingual clinical ontology (`data/nepali_clinical_lexicon.json`)

---

## 🚀 Running Sanchai Locally

### 1. Backend Setup & Startup

```bash
# Clone repository and enter folder
cd Sanchai

# Install Python dependencies
pip install -r backend/requirements.txt
pip install "fhir.resources>=7.1.0" reportlab

# Seed the database (creates data/sanchai.db with 261 concepts and 3 patients)
python -m backend.seed

# Run the FastAPI server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Verify backend health:
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Frontend Setup & Startup

```bash
# In a separate terminal, navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## 🧭 Page Routes & UI Capabilities

- **`http://localhost:3000/`** — Product landing, overview metrics, operating modes, and quick actions.
- **`http://localhost:3000/intake`** — Interactive Intake Studio with quick presets, live document processing, Tier 1/2/3 concept badges, and the Approval-Before-Write gate.
- **`http://localhost:3000/patients/patient_ram`** — Longitudinal patient ledger showing confirmed allergies, active conditions, encounters timeline, and links to:
  - 📄 **Doctor Summary PDF:** `GET /api/v1/patients/{id}/summary.pdf`
  - ⚡ **HL7 FHIR R4 Bundle:** `GET /api/v1/patients/{id}/fhir`
  - 🚨 **Emergency QR Code:** `GET /api/v1/patients/{id}/qr.png`
- **`http://localhost:3000/scan`** — Interactive QR decoder and emergency card simulator.
- **`http://localhost:3000/emergency/[token]`** — Lightweight, offline-ready emergency triage summary for first responders.
- **`http://localhost:3000/evidence`** — Live NepClinBench dashboard with real-time benchmark execution button, distribution breakdown, and ablation comparison table.

---

## 🧪 Testing

Run the comprehensive 48-test backend test suite:
```bash
pytest
```

---

## 📄 License & Safety Notice

Distributed under the MIT License. Clinical data concepts are research drafts designed to empower patient health agency and improve doctor communication. Authoritative ledger commits strictly require human-in-the-loop approval.
