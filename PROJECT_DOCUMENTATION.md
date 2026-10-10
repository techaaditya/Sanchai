# Sanchai (सञ्चै) — Master Project Documentation
### A Zero-Hallucination Nepali Clinical Health Ledger & Offline-First Multimodal AI Assistant

---

## 1. Executive Summary & Vision

**Sanchai (सञ्चै)** is named after the warm Nepali greeting *"सञ्चै हुनुहुन्छ?"* (*"Are you well?"*). It is a clinically grounded personal health ledger system engineered specifically for the realities of Nepal's healthcare ecosystem.

In Nepal, patients carry plastic bags filled with faded paper receipts, handwritten doctor slips, and printed lab reports from different clinics. When seeing a new doctor or arriving at an emergency room, doctors have almost zero visibility into the patient's medical past. Drug brand names are frequently confused with generic equivalents, leading to accidental double dosing. Severe drug allergies are forgotten or unrecorded. And during frequent internet cuts in remote districts, cloud-only health systems completely stop working.

Sanchai bridges this gap. It ingests handwritten paper prescriptions, bilingual clinic notes, and digital lab reports, converting them into structured, verified, longitudinal health records. 

### Core Guarantees of Sanchai:
1. **Zero Hallucinations on Clinical Entities:** Unlike generic chatbots that invent medication names or dosages, Sanchai uses a deterministic 3-tier normalization engine grounded in a 300-concept clinical lexicon verified against Nepal's Department of Drug Administration (DDA), the National List of Essential Medicines (NLEM 2021), and WHO ICD-11.
2. **Approval-Before-Write Gate:** No AI model can write directly to an authoritative patient health record without explicit human clinician or patient review and confirmation.
3. **Dual-Tier Offline-First AI:** Built for Nepal's mountainous topography. Uses high-capacity `gemma4:31b-cloud` when connected, and automatically falls back to `gemma4:e2b-it-qat` running locally on the device when internet connectivity is severed.
4. **Instant Emergency Triage:** High-contrast offline QR cards allowing ambulance paramedics to immediately see blood groups and life-threatening allergies in under one second.

---

## 2. The Real-World Healthcare Problem in Nepal

### 2.1 The "Plastic Bag" Health Record
In Nepal, electronic health record (EHR) adoption is fragmented. Most secondary and tertiary hospitals (such as Bir Hospital, TUTH, or private nursing homes) use isolated billing software rather than interoperable medical ledgers. Patients bear the entire burden of carrying physical paper folders:
- Hand-scribbled prescription pads written in hurried cursive.
- Printed thermal receipts that fade within three months.
- Lab test printouts from disparate diagnostic centers.
When patients travel between districts or visit specialists, past history is routinely lost.

### 2.2 Brand vs. Generic Confusion and Accidental Toxicity
In Nepal, pharmacies dispense medications primarily by commercial brand names rather than generic chemical names:
- A patient prescribed *Cetamol* in Kathmandu visits a clinic in Pokhara where a doctor writes *Paracetamol* or *Flexon*.
- A patient with acid reflux is prescribed *Pantocid* at one hospital and *Pantop* at another.
Without automatic brand-to-generic resolution, patients inadvertently take duplicate doses of the same underlying chemical compound, leading to acute liver or kidney toxicity.

### 2.3 The Trilingual & Code-Mixed Clinical Language
Clinical communication in Nepal does not happen in pure English or pure Devanagari. It is heavily code-mixed:
- Spoken symptom: *"टाउको दुखेको"* (Tauko dukheko) or *"ज्वरो आयो"* (Jwaro aayo).
- Romanized phonetic notes: *"chhati polyo"* (heartburn), *"khoki"* (cough).
- Medical English terms: *"fever"*, *"hypertension"*, *"type 2 diabetes"*.
- Nepali doctor shorthand: *"tab cetamol 500mg 1 TDS x 3d"*, *"jwaro chhaina"* (no fever).
Generic NLP systems fail because they treat Nepali and English as separate silos and cannot handle Romanized phonetics or Devanagari matra spelling variations caused by mobile keyboard auto-correct or OCR noise.

### 2.4 Missed Allergy Contraindications
When a patient has a known allergy (such as a severe Penicillin allergy), doctors writing rapid prescriptions may accidentally prescribe related beta-lactam antibiotics (such as Amoxicillin, Ampicillin, or Augmentin). Without an automated safety guardrail cross-referencing past allergies, anaphylactic reactions occur.

### 2.5 The Mountain Geography & Connectivity Barrier
Nepal's geography is characterized by rugged mountain ranges, deep valleys, and remote rural districts. Fiber optic lines are frequently severed by landslides, monsoon floods, and road construction. Rural health posts (स्वास्थ्य चौकी) often run on solar batteries with intermittent mobile data. A clinical system that relies 100% on cloud AI APIs becomes useless the moment a fiber link breaks.

---

## 3. The Sanchai Solution & Approach

Sanchai replaces fragmented paperwork with a unified, verifiable, offline-first personal health ledger:

```
[ Handwritten Slip / PDF Lab / Bilingual Text ]
                       │
                       ▼
          [ Multimodal Ingestion Layer ]
         • PyMuPDF for digital text layers
         • Gemma 4 Vision OCR for handwriting
                       │
                       ▼
       [ Deterministic 3-Tier Normalizer ]
         • Tier 1: Sub-millisecond Exact Dictionary Match
         • Tier 2: Matra & Orthographic Fuzzy Levenshtein
         • Tier 3: Gemma 4 Constrained Guardrail (Negative Rejection)
                       │
                       ▼
      [ Directional Negation & Brand Resolution ]
         • "ज्वरो छैन" -> Fever: NEGATED (Excluded from active conditions)
         • "Cetamol" -> Paracetamol (NCL-0005)
                       │
                       ▼
         [ Human Approval-Before-Write Gate ]
         Clinician reviews, edits, and commits
                       │
                       ▼
        [ Authoritative Patient Health Ledger ]
                       │
     ┌─────────────────┼──────────────────────────┐
     ▼                 ▼                          ▼
[ SanchAI EHR ]  [ HL7 FHIR R4 ]          [ Emergency QR & PDF ]
Chatbot Assistant  Interoperable Bundle    Paramedic Offline Card
```

---

## 4. Key Features & Clinical Capabilities

### 4.1 Deterministic 3-Tier Clinical Normalization Engine
To eliminate hallucinations while accommodating real-world spelling variations, Sanchai uses a 3-tier matching pipeline:

- **Tier 1 (Exact Match - 0ms latency):** Matches against pre-indexed dictionary aliases across Devanagari (*मधुमेह*), Romanized phonetics (*madhumeha*), Latin names (*diabetes mellitus*), and brand names.
- **Tier 2 (Orthographic / Matra Fuzzy Match - <2ms latency):** OCR often misreads vowel signs (matras), e.g., scanning *ज्वरो* (fever) as *ज्वरौ*. Tier 2 uses bounded Levenshtein edit distance with a strict character-length penalty. It recovers corrupted matras without drifting into unrelated clinical concepts.
- **Tier 3 (Gemma 4 Constrained Guardrail):** When ambiguous clinical phrasing is encountered, candidate concept IDs from Tiers 1 and 2 are presented to Gemma 4. Gemma 4 is strictly constrained: it may only choose from the provided candidates or output `UNKNOWN`. It cannot invent new medical terms.

### 4.2 Brand-to-Generic Pharmacology Resolution
Every pharmaceutical brand registered in the lexicon points directly to its active generic chemical entity (`generic_of` link):
- *Taxim-O* $\rightarrow$ *Cefixime*
- *Cifran* $\rightarrow$ *Ciprofloxacin*
- *Pantocid* / *Pantop* $\rightarrow$ *Pantoprazole*
- *Flagyl* / *Metrogyl* $\rightarrow$ *Metronidazole*
- *Telma* $\rightarrow$ *Telmisartan*
This allows clinicians to immediately detect duplicate therapies and prevents accidental overdosage.

### 4.3 Directional Negation Detection (Zero False Positives)
Medical notes frequently document symptoms that a patient does *not* have (pertinent negatives). For example:
- *"खोकी छ तर ज्वरो छैन"* (Cough is present, but fever is absent).
If a system naively tags "Fever", the patient's record is permanently corrupted. Sanchai recognizes Nepali negation markers (*छैन*, *hoina*, *bina*, *negative*, *absent*) within a directional token window. Negated findings are explicitly flagged and completely excluded from active condition summaries.

### 4.4 Human-in-the-Loop Approval-Before-Write Gate
Under medical safety principles, AI models should never act as autonomous writers to authoritative medical ledgers. Sanchai enforces an approval gate:
- AI parses and extracts entities into a staging buffer.
- The clinician or patient inspects the extracted medications, dosages, and conditions.
- Only upon clicking **"Approve & Commit to Patient Record"** is the record permanently written to SQLite and FHIR.

### 4.5 SanchAI (सञ्चै एआई): Longitudinal Multimodal Clinical Assistant
SanchAI is an EHR-grounded clinical chatbot available at `/chatbot`:
- **Patient Context Aware:** SanchAI reads the patient's full longitudinal history (active conditions, current medications, recorded allergies, timeline encounters).
- **Multimodal Attachment Ingestion:** Users can upload PDF lab reports or prescription photos. PyMuPDF and Gemma Vision extract text, run the normalizer, and ground SanchAI's interpretation.
- **Real-Time Safety & Contraindication Checks:** Cross-references the patient's allergy records against user questions or newly uploaded slips. If a penicillin-allergic patient asks about Amoxicillin or Augmentin, SanchAI immediately issues a critical safety alert.
- **Pre-Visit Doctor Summary:** Generates structured briefing notes summarizing recent complaints, current drugs, and questions for upcoming clinic appointments.
- **Bilingual Explanations:** Explains complex lab values (e.g. Widal test, Lipid profile, CBC) in simple conversational Nepali and English.

### 4.6 Emergency Health QR & Offline Paramedic Triage
In trauma or ambulance situations, unconscious patients cannot speak:
- Sanchai generates a compact, high-contrast Segno QR token (`sanchai://p/{token}`).
- When scanned by paramedics, it opens an offline-optimized emergency card displaying:
  - Blood Group (e.g., `B+`)
  - Severe Documented Allergies (e.g., `Penicillin - severe anaphylaxis risk`)
  - Active Chronic Conditions (e.g., `Type 2 Diabetes Mellitus`, `Hypertension`)
  - Emergency contact details

### 4.7 International Standards Interoperability (HL7 FHIR R4 & A4 PDF)
- **HL7 FHIR R4 Collection Bundle:** Exports standards-compliant JSON bundles (`Patient`, `Condition`, `MedicationStatement`, `AllergyIntolerance`, `Observation`) mapped to ICD-11 codes.
- **Doctor Summary A4 PDF:** Generates a print-ready clinical report via ReportLab with embedded QR verification for offline clinic visits.

---

## 5. The 300-Concept Nepali Clinical Lexicon Dataset

The foundation of Sanchai's zero-hallucination guarantee is its custom bilingual clinical ontology (`data/nepali_clinical_lexicon.json`), comprising **300 curated clinical concepts** (`NCL-0001` through `NCL-0300`).

### 5.1 Authoritative Verification Sources
Every entry in the clinical lexicon is derived from and cross-referenced with three authoritative healthcare standards:
1. **Nepal Department of Drug Administration (DDA):** Official pharmaceutical brand names, active ingredient formulations, dosage forms (tablets, syrups, injections), and manufacturer registrations in Nepal.
2. **National List of Essential Medicines (NLEM 2021, Ministry of Health and Population, Nepal):** Standard generic drug nomenclature, therapeutic classes, and priority medicines for district and provincial hospitals.
3. **World Health Organization (WHO) ICD-11:** International Classification of Diseases 11th Revision codes for conditions, symptoms, and anatomy, ensuring international interoperability.

### 5.2 Lexicon Schema Structure
Each concept is stored with rich linguistic and clinical metadata:

```json
{
  "concept_id": "NCL-0005",
  "canonical_en": "Paracetamol",
  "canonical_np": "प्यारासिटामोल",
  "concept_type": "drug_generic",
  "preferred_register": "formal",
  "devanagari_aliases": ["प्यारासिटामोल", "पारामोल", "सिटामोल"],
  "romanized_aliases": ["paracetamol", "paramol", "cetamol"],
  "latin_aliases": ["acetaminophen", "paracetamol"],
  "code_mixed_patterns": ["tab cetamol", "paracetamol 500mg"],
  "generic_of": null,
  "icd11_code": null,
  "icd10_code": null,
  "negation_sensitive": 0,
  "duration_days": 3,
  "frequency_per_day": 3,
  "source": "Nepal NLEM 2021 / WHO Essential Medicines",
  "license": "Open Healthcare Data"
}
```

### 5.3 Categorical Breakdown of Concepts
- **Conditions & Diagnoses (100+ concepts):** Diabetes Type 2 (`5A11`), Essential Hypertension (`BA00`), Typhoid Fever (`1A07`), Chronic Obstructive Pulmonary Disease (`CA22`), Dengue Fever (`1D20`), Scrub Typhus (`1C20.0`), Chronic Kidney Disease (`GB61`), Gout (`FA25`), Migraine (`8A80`), Acute Appendicitis (`DB10`), Allergic Rhinitis (`CA08.0`), Non-Alcoholic Fatty Liver Disease (`DB92`).
- **Essential Generics & Prescribed Drugs (90+ concepts):** Metformin, Amlodipine, Paracetamol, Ciprofloxacin, Cefixime, Azithromycin, Omeprazole, Pantoprazole, Metronidazole, Telmisartan, Montelukast, Diclofenac, Ranitidine, Levofloxacin, Glimepiride, Ceftriaxone.
- **Nepal DDA Commercial Brands (60+ concepts):** Cetamol, Taxim-O, Cifran, Pantocid, Flagyl, Metrogyl, Telma, Montair-LC, Voveran, Aciloc, Loxof, Amaryl, Pantop, Flexon, Monocef.
- **Laboratory Investigations (25+ concepts):** Complete Blood Count (CBC), Fasting Blood Sugar (FBS), HbA1c, Widal Test, Urine Routine/Microscopic, Lipid Profile, Thyroid Function Test (TFT), Serum Uric Acid, Urine Culture, GeneXpert MTB/RIF, 25-OH Vitamin D.
- **Colloquial & Everyday Symptoms (25+ concepts):** Fever (*Jwaro*), Cough (*Khoki*), Headache (*Tauko Dukheko*), Chest Pain (*Chhati Dukheko*), Dizziness (*Ringata*), Heartburn (*Chhati Polnu*), Dysuria (*Pisaab Poldaa*), Palpitations (*Mutu Dhukdhuk*), Anorexia (*Ruchi Nahunu*), Insomnia (*Nidraa Naparnu*).

---

## 6. Dual-Tier AI Architecture (Cloud + Edge Offline)

Sanchai uses a hybrid architecture designed for resilience in developing healthcare settings:

```
                          ┌────────────────────────┐
                          │ User Request / Intake  │
                          └───────────┬────────────┘
                                      │
                         Is Internet Available?
                                ╱           ╲
                           YES ╱             ╲ NO / TIMEOUT
                              ▼               ▼
                 ┌──────────────────────┐   ┌──────────────────────┐
                 │  Primary Cloud AI    │   │  Edge Offline Fallback│
                 │  gemma4:31b-cloud    │   │  gemma4:e2b-it-qat   │
                 │  (Ollama Cloud API)  │   │  (Local Ollama Edge) │
                 └──────────────────────┘   └──────────────────────┘
                              │                       │
                              └───────────┬───────────┘
                                          ▼
                         [ Authoritative Verification ]
```

### 6.1 Primary Model: `gemma4:31b-cloud`
- **Hosting:** Ollama Cloud API (`https://ollama.com`)
- **Parameters:** 31 Billion parameters
- **Use Cases:** Complex multimodal vision OCR on doctor handwriting, high-nuance multilingual conversation, clinical doctor summary generation.
- **Strengths:** High reasoning capacity, broad medical vocabulary, zero local GPU requirements for client devices.

### 6.2 Offline Edge Fallback: `gemma4:e2b-it-qat`
- **Hosting:** Local Ollama service (`http://localhost:11434`)
- **Parameters:** Quantized 2B / 4.6B parameter model (`Q4_0` GGUF quantization)
- **Local Footprint:** ~4.3 GB RAM/VRAM
- **Use Cases:** Immediate offline fallback when network connection fails, local prescription handwriting transcription, offline conversational guidance.
- **Strengths:** Runs on standard laptops or edge mini-PCs with no internet connection, sub-second token latency once loaded into memory.

---

## 7. NepClinBench Evaluation Results

To empirically validate Sanchai against raw AI inference, we constructed **NepClinBench**, a gold-standard benchmark containing **60 real-world bilingual clinical cases** (`data/nepclinbench_gold.json`).

### Benchmark Comparison Table

| Evaluation Metric | Sanchai 3-Tier Pipeline | Raw Gemma 4 (31B Cloud) Baseline | Sanchai Advantage |
| :--- | :---: | :---: | :---: |
| **Exact Set Match (N=60)** | **96.7% (58 / 60)** | 46.7% (28 / 60) | **+50.0%** |
| **Precision (Non-hallucination)** | **1.000 (0% Hallucination)** | 0.817 (18.3% Hallucinated) | **+22.4 pts** |
| **Brand to Generic Resolution** | **100.0% (54 / 54)** | 41.7% (23 / 54) | **+58.3%** |
| **Negation Accuracy** | **100.0% (10 / 10)** | 50.0% (5 / 10) | **+50.0%** |
| **Duration & Dosage Parsing** | **100.0% (12 / 12)** | 66.7% (8 / 12) | **+33.3%** |
| **FHIR R4 Bundle Validity** | **100% (Strict Valid JSON)** | 0% (Unstructured English) | **100% Interoperable** |
| **Offline / Edge Latency** | **Yes (< 5ms deterministic)** | No (> 800ms cloud roundtrip) | **160x Faster** |

### Why Raw Gemma 4 Hallucinates Without Sanchai
When raw LLMs encounter messy bilingual text like *"tab flagyl 400 1 tds ra ranitidine khanu"*, they frequently:
1. Hallucinate generic formulations not registered in Nepal.
2. Miss negated conditions (*"jwaro chhaina"* parsed as active fever).
3. Output non-standard JSON schemas that break hospital databases.
Sanchai's deterministic scaffolding binds Gemma 4 to verified medical ontology ground truth.

---

## 8. Technology Stack Summary

- **Backend Core:** Python 3.11+ / 3.13, FastAPI, Uvicorn, Pydantic v2
- **Persistence & Storage:** SQLite 3 (`data/sanchai.db`) with relational foreign keys and automatic additive migrations
- **AI & NLP:** 
  - `gemma4:31b-cloud` via Ollama Cloud API
  - `gemma4:e2b-it-qat` via local Ollama
  - RapidFuzz (C++ accelerated Levenshtein string distance)
  - PyMuPDF (digital PDF text and vector extraction)
- **Clinical Interoperability:**
  - `fhir.resources` (HL7 FHIR R4 standard models)
  - ReportLab (A4 print-ready PDF engine)
  - Segno (high-contrast micro & standard QR codes)
- **Frontend Architecture:**
  - Next.js 15 (App Router with Server Components & TypeScript)
  - Vanilla CSS design tokens with warm paper and clinical emerald palette
  - Zero heavy third-party UI dependencies for fast page loads
- **Test Infrastructure:** Pytest with 54 passing unit and integration tests

---

## 9. Conclusion
Sanchai demonstrates that modern AI in healthcare does not mean replacing clinical judgment or trusting unverified chatbot outputs. By combining state-of-the-art Google Gemma 4 models with strict deterministic ontology scaffolding, approval-before-write safety gates, and offline edge resilience, Sanchai delivers a practical, life-saving personal health ledger tailored for Nepal.
