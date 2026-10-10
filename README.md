# Sanchai (सञ्चै)
### Zero-Hallucination Nepali Clinical Health Ledger & Multimodal Ingestion Engine

**Sanchai (सञ्चै)** — named after the warm Nepali greeting *"सञ्चै हुनुहुन्छ?"* (*"Are you well?"*) — is a clinically grounded personal health ledger system designed specifically for Nepal's healthcare ecosystem. It ingests handwritten doctor prescriptions, bilingual clinic notes, and digital lab reports, converting them into structured, longitudinal medical histories with **zero hallucinations** on verified clinical entities.

---

## 🎯 Key Differentiators & Clinical Capabilities

1. **Deterministic 3-Tier Clinical Normalization:**
   - **Tier 1 (Exact Match):** Direct sub-millisecond mapping across Devanagari, Romanized phonetics, and Latin brand aliases in the 261-concept clinical lexicon (`data/nepali_clinical_lexicon.json`).
   - **Tier 2 (Orthographic / Matra Fuzzy):** Levenshtein distance bounded by strict edit-budgets, recovering OCR-corrupted vowel signs (*"ज्वरौ"* $\rightarrow$ *ज्वरो*).
   - **Tier 3 (Gemma 4 Guardrail):** Constrained candidate selection using `gemma4:31b-cloud` (via Ollama Cloud API) restricted strictly to registered lexicon IDs with negative rejection.
2. **Brand-to-Generic Pharmacology Resolution:**
   - Automatically translates everyday brand prescriptions (*Cetamol* $\rightarrow$ *Paracetamol*, *Taxim-O* $\rightarrow$ *Cefixime*, *Cifran* $\rightarrow$ *Ciprofloxacin*, *Pantocid* $\rightarrow$ *Pantoprazole*), preventing duplicate dosing and dangerous drug interactions across fragmented health visits.
3. **Directional Negation Detection (Zero False Positives):**
   - Automatically recognizes Nepali negation markers (*"छैन"*, *"hoina"*, *"bina"*). Denied symptoms (e.g., *"ज्वरो छैन"* $\rightarrow$ Fever: Negated) are strictly excluded from active patient conditions.
4. **Approval-Before-Write Gate:**
   - Human-in-the-loop safety protocol: No AI output writes directly to authoritative patient health records without explicit clinician/patient review and confirmation.
5. **Multimodal Intake (Zero Cloud Latency for Digital Assets):**
   - **Digital PDFs & Lab Reports:** Extracted instantly via PyMuPDF.
   - **Handwritten Prescriptions & Clinic Slips:** Vision OCR transcription via `gemma4:31b-cloud`.
   - **Bilingual Text & Romanized Notes:** Processed instantly via the 3-tier normalization engine.
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
- **Backend Framework:** FastAPI, Uvicorn, Python 3.11+ / 3.13
- **Data Persistence:** SQLite (`data/sanchai.db`), Pydantic v2
- **Document & Clinical Engines:** PyMuPDF, ReportLab, Segno, `fhir.resources`
- **Frontend Architecture:** Next.js 15 (App Router), TypeScript, Vanilla CSS design tokens
- **Ontology Core:** Curated 261-concept bilingual clinical ontology (`data/nepali_clinical_lexicon.json`)

---

## ⚙️ Environment Configuration

Create a `.env` file in the project root (copied from `.env.example`):

```bash
# Copy example environment configuration
cp .env.example .env
```

Ensure your `.env` contains your Ollama Cloud credentials:

```dotenv
# Backend Configuration
PORT=8000
MODEL_BACKEND=cloud
OLLAMA_CLOUD_URL=https://ollama.com
MODEL_NAME=gemma4:31b-cloud
OLLAMA_API_KEY=your_actual_ollama_api_key_here
DB_PATH=./data/sanchai.db

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 🚀 How to Run Sanchai Independently

Follow these simple steps to run the complete stack on your machine.

### Prerequisites
- **Python 3.11+** installed (`python --version`)
- **Node.js 18+** & **npm** installed (`node -v`, `npm -v`)
- Active Internet connection for `gemma4:31b-cloud` Ollama Cloud inference

---

### Step 1: Initialize Database & Install Backend Dependencies

Open a terminal in the root directory `Sanchai`:

```bash
# 1. Install backend Python dependencies
pip install -r backend/requirements.txt

# 2. Seed the clinical database (initializes data/sanchai.db with 261 concepts and 3 patients)
python -m backend.seed
```

---

### Step 2: Start the FastAPI Backend Server

In your first terminal, run:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **API Documentation & Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Probe:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

You should see:
```json
{
  "status": "ok",
  "service": "sanchai-api",
  "model_backend": "cloud",
  "model": "gemma4:31b-cloud",
  "services": [
    { "service": "db", "status": "up" },
    { "service": "gemma_model", "status": "up" }
  ]
}
```

---

### Step 3: Start the Next.js Frontend

Open a **second terminal** and navigate to the `frontend` folder:

```bash
cd frontend

# Install frontend dependencies (if not already installed)
npm install

# Start Next.js development server
npm run dev
```

The application is now accessible at:
👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🧭 Page Routes & End-to-End Walkthrough

| Route | Purpose & Clinical Actions |
| :--- | :--- |
| **`http://localhost:3000/`** | **Home & Health Dashboard:** Overview metrics, patient ledger count, operating modes, and quick launch links. |
| **`http://localhost:3000/intake`** | **Intake Studio & Approval Gate:**<br>• Try demo presets (Prescription slip, clinic note with negation, printed lab report).<br>• Real-time 3-tier concept extraction badges (Tier 1 exact, Tier 2 fuzzy, Tier 3 Gemma 4).<br>• Drug brand-to-generic mapping indicator.<br>• **Approve & Commit to Patient Record** button: writes verified record to patient ledger. |
| **`http://localhost:3000/patients/patient_ram`** | **Longitudinal Patient Ledger:**<br>• Demographics, blood group, allergies safety alert, active conditions.<br>• Chronological clinical encounters timeline.<br>• 📄 **Download Doctor Summary PDF** button (`GET /api/v1/patients/{id}/summary.pdf`).<br>• ⚡ **View HL7 FHIR R4 Bundle** button (`GET /api/v1/patients/{id}/fhir`).<br>• 🚨 **Open Emergency Summary** link. |
| **`http://localhost:3000/scan`** | **Emergency QR Scanner Simulator:**<br>• Camera viewfinder simulation with corner targeting.<br>• One-click demo buttons for preloaded patients (Ram Bahadur, Sita Kumari, Hari Prasad).<br>• Direct token input and optical triage decoder. |
| **`http://localhost:3000/emergency/[token]`** | **First-Responder Emergency Triage View:**<br>• High-contrast optical QR code rendered via Segno.<br>• Immediate offline triage: blood group, severe allergies, and contraindicated medications. |
| **`http://localhost:3000/evidence`** | **NepClinBench Evaluation Dashboard:**<br>• Run live 60-item clinical benchmark evaluation in one click.<br>• Real-time accuracy breakdown across condition, symptom, medication, and anatomy concepts.<br>• Full ablation table comparing Sanchai 3-Tier against raw Gemma 4 baseline. |

---

## 🧪 Automated Testing & Verification

### Run Backend Unit & Integration Tests (48 Tests)
```bash
python -m pytest
```
*Expected: 48 passed (tests database seeding, FHIR bundling, intake normalization, approval-before-write gate, and emergency QR generation).*

### Run Frontend Production Build & TypeScript Typecheck
```bash
cd frontend
npm run build
```
*Expected: Compiled successfully with 0 errors across all 7 routes.*

---

## 📂 Project Structure

```text
Sanchai/
├── backend/
│   ├── main.py                  # FastAPI application entrypoint & health probe
│   ├── config.py                # Pydantic settings loading from .env
│   ├── schemas.py               # Pydantic v2 clinical request/response contracts
│   ├── seed.py                  # Database initialization and demo patient seed
│   ├── normalization/
│   │   ├── engine.py            # 3-Tier normalization engine
│   │   ├── matcher.py           # RapidFuzz & exact matcher
│   │   └── guardrail.py         # Constrained Gemma 4 fallback
│   ├── ingestion/
│   │   ├── pipeline.py          # Multimodal ingestion orchestrator
│   │   ├── ocr.py               # Vision OCR integration
│   │   └── pdf.py               # PyMuPDF digital document extractor
│   ├── record/
│   │   ├── db.py                # SQLite database session & queries
│   │   ├── fhir.py              # HL7 FHIR R4 Collection Bundle generator
│   │   ├── qr.py                # Segno high-contrast emergency QR generator
│   │   └── pdf.py               # ReportLab Doctor Summary A4 PDF generator
│   ├── routers/
│   │   ├── intake.py            # Intake endpoints (text, image, pdf)
│   │   ├── patients.py          # Patient ledger, approval gate, FHIR, PDF, QR
│   │   └── eval.py              # NepClinBench evaluation endpoints
│   └── requirements.txt         # Python dependencies
├── data/
│   ├── nepali_clinical_lexicon.json  # 261 curated bilingual clinical concepts
│   └── nepclinbench_gold.json        # 60 gold-standard clinical evaluation cases
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Home dashboard
│   │   ├── intake/page.tsx      # Multimodal Intake Studio & Approval Gate
│   │   ├── patients/[id]/       # Longitudinal patient ledger
│   │   ├── scan/page.tsx        # Emergency QR Scanner
│   │   ├── emergency/[token]/   # Offline-ready triage view
│   │   └── evidence/page.tsx    # NepClinBench evaluation dashboard
│   ├── components/              # Shell, metrics, navigation, approval actions
│   └── lib/
│       ├── api.ts               # Dynamic API client with fallback base URL
│       └── frontend-data.ts     # Server-side data fetching utilities
├── tests/                       # 48 pytest test suites
├── .env.example                 # Example configuration
└── README.md                    # System documentation and execution guide
```

---

## 📄 License & Safety Notice

Distributed under the **MIT License**. Clinical data concepts and evaluations are research prototypes designed to empower patient health agency and improve doctor communication. Authoritative ledger commits strictly require human-in-the-loop clinician approval.
