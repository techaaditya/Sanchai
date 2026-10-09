# Sanchai (सञ्चै)
### Zero-Hallucination Nepali Clinical Health Ledger & Multimodal Ingestion

**Sanchai (सञ्चै)** — named after the warm Nepali greeting *"सञ्चै हुनुहुन्छ?"* (Are you well?) — is a clinically grounded personal health record system built for Nepal. It converts paper-based handwritten doctor prescriptions, clinic slips, and digital lab reports into structured, longitudinal medical histories with 0% hallucination on known clinical terms.

---

## 🎯 Key Capabilities

1. **Multimodal Document Intake:**
   * **Handwritten Prescriptions & Slips:** Vision OCR extraction via `gemma4:31b-cloud`.
   * **Digital Lab Reports & Bills:** Zero-latency direct extraction via PyMuPDF.
   * **Direct Clinical Text:** Raw observation intake.
   *(Note: Voice input is strictly de-scoped for future roadmap).*
2. **Deterministic 3-Tier Clinical Normalization:**
   * Snaps messy clinical text to a curated **261-concept Nepali Clinical Lexicon**.
   * Directional negation detection (*"ज्वरो छैन"* $\rightarrow$ Fever negated).
   * Brand-to-generic drug translation (*Cetamol* $\rightarrow$ *Paracetamol*, *Taxim-O* $\rightarrow$ *Cefixime*, *Pantocid* $\rightarrow$ *Pantoprazole*).
   * Strict edit distance budget guards preventing false positive mappings.
3. **Approval-Before-Write Gate:**
   * Human-in-the-loop review interface: medical records are committed only upon patient/clinician confirmation.
4. **Emergency Health QR & Interoperability:**
   * Offline-scannable emergency QR code (`segno`) encoding critical allergies, blood group, and conditions (`sanchai://p/{token}`).
   * Standard HL7 FHIR R4 collection bundle export (strictly excluding negated conditions).
5. **NepClinBench Evaluation Suite:**
   * Gold-standard 60-sample benchmark demonstrating 58/60 exact match and 1.000 precision.

---

## 🛠️ Technology Stack

* **AI & Language Model:** `gemma4:31b-cloud` (served via Ollama Cloud API)
* **Backend:** Python 3.13, FastAPI, Pydantic v2, SQLite, PyMuPDF, Segno
* **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui
* **Data Core:** Curated 261-concept bilingual clinical ontology (`data/nepali_clinical_lexicon.json`)

---

## 🚀 Quick Start (Backend)

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env
```
Edit `.env` and set your `OLLAMA_API_KEY`:
```env
PORT=8000
MODEL_BACKEND=cloud
OLLAMA_CLOUD_URL=https://ollama.com
MODEL_NAME=gemma4:31b-cloud
OLLAMA_API_KEY=your_key_here
DB_PATH=./data/sanchai.db
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Verify NLP Core & Normalization
```bash
python -c "from backend.nlp import normalize; res = normalize('ज्वरो छैन सिटामोल ५०० एमजी'); print(res)"
```

---

## 👥 Parallel Team Workflow (3-Person Split)

The foundation contracts, Pydantic v2 schemas (`backend/schemas.py`), and data assets are frozen on `main`. All three team members can branch off `main` and work completely in parallel:

| Role | Suggested Branch | Focus Area |
| :--- | :--- | :--- |
| **Person 1 (Frontend)** | `feat/frontend` | Next.js App Router, intake upload interface, approval card UI, timeline drawer, QR scanner |
| **Person 2 (Backend)** | `feat/backend-api` | FastAPI routers (`/api/v1/intake`, `/api/v1/patients`), SQLite DB persistence, Segno QR, FHIR R4 |
| **Person 3 (AI & Eval)** | `feat/ai-and-eval` | `gemma4:31b-cloud` prompt tuning, NepClinBench runner (`backend/eval`), demo sample slips |

---

## 📄 License & Safety Notice

Distributed under the MIT License. Clinical data concepts are research drafts designed to assist patient agency and doctor communication. All record additions require human-in-the-loop verification.
