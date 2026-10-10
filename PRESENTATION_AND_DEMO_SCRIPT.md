# Sanchai (सञ्चै) — 5-Minute Pitch Slides & Live Demo Script

Total Time Allocation:
- Presentation Slides: 3 Minutes (0:00 - 3:00)
- Live Interactive Demo: 2 Minutes (3:00 - 5:00)

---

# Part 1: Slide-by-Slide Presentation (3 Minutes)

### Slide 1: Title & Hook
- **Headline:** Sanchai (सञ्चै)
- **Subheadline:** The Zero-Hallucination Health Ledger for Nepal
- **Visuals:** Warm paper background, clean emerald emblem, typography reading "सञ्चै हुनुहुन्छ?"
- **Speaker Timing:** 0:00 - 0:30

**Spoken Script:**
"Namaste everyone. In Nepali, when we meet someone we care about, we ask: 'Sanchai hunuhunchha?' Are you well?

Yet across Nepal today, staying well is burdened by paper. Patients carry plastic bags filled with faded doctor receipts, handwritten prescription slips, and scattered lab reports. When they travel between clinics or visit an emergency room, their past medical history is completely lost.

Doctors are forced to treat patients blind, leading to accidental double dosing, unrecorded allergies, and preventable medical tragedies. 

Today, we introduce Sanchai: the zero-hallucination, offline-first personal health ledger built specifically for Nepal."

---

### Slide 2: The Core Problem in Nepal
- **Headline:** The Reality of Healthcare in Nepal
- **Key Points on Slide:**
  - Plastic Bag Records: Faded paper receipts and lost medical history
  - Brand Confusion: Patients taking Cetamol and Paracetamol simultaneously
  - Trilingual Chaos: Notes mixed in Devanagari, English, and Romanized slang
  - Connectivity Barrier: Internet lines frequently cut in rural mountain clinics
- **Speaker Timing:** 0:30 - 1:00

**Spoken Script:**
"Why do generic digital health apps fail in Nepal? Because they ignore four ground realities:

First: The plastic bag problem. Paper records fade and get lost within months.

Second: The brand trap. Pharmacies dispense medicines by commercial brand names. A patient taking Cetamol in Kathmandu is prescribed Paracetamol in Pokhara, resulting in toxic accidental overdoses.

Third: Language complexity. Doctors and patients do not speak in pure medical textbook English. They write in a mix of Nepali Devanagari, Romanized phonetics, and medical shorthand.

And fourth: The mountain connectivity barrier. In district health posts and mountain roads, internet lines frequently cut out. A cloud-only app is completely useless when a landslide severs the fiber line."

---

### Slide 3: The Sanchai Architecture
- **Headline:** Engineered for Clinical Safety
- **Key Points on Slide:**
  - 3-Tier Normalization: Zero hallucinations guaranteed
  - 300 Verified Concepts: Sourced from Nepal DDA, NLEM 2021, and WHO ICD-11
  - Approval Before Write: Human clinician reviews every entry before saving
  - Dual-Tier AI: Cloud Gemma 4 (31B) with instant local offline fallback (Gemma 4 QAT)
- **Speaker Timing:** 1:00 - 1:45

**Spoken Script:**
"To solve this safely, we built Sanchai around clinical ground truth.

Unlike generic chatbots that guess or hallucinate dosages, Sanchai uses a deterministic 3-tier normalization engine. 

Tier 1 matches exact names in under one millisecond. 
Tier 2 fixes handwriting OCR spelling mistakes using bounded phonetic distance. 
And Tier 3 uses Google Gemma 4 strictly as a constrained guardrail with negative rejection. It can only pick verified medical IDs or say 'Unknown'.

Every single concept is grounded in our 300-concept bilingual lexicon verified directly against the Nepal Department of Drug Administration, the National List of Essential Medicines, and WHO ICD-11.

Crucially, no AI writes directly to a patient record. We enforce a strict human-in-the-loop approval gate. And if the internet cuts out, our system seamlessly falls back to a locally installed, quantized Gemma 4 model running directly on the device."

---

### Slide 4: Empirical Proof & Performance
- **Headline:** NepClinBench Live Evaluation
- **Key Metrics on Slide:**
  - Exact Set Match: 96.7% vs 46.7% for raw Gemma 4 (+50% gain)
  - Precision / Non-Hallucination: 1.000 (0% Hallucination rate)
  - Negation Accuracy: 100% (Correctly recognizing 'Jwaro chhaina' as no fever)
  - Deterministic Speed: Under 5 milliseconds offline
- **Speaker Timing:** 1:45 - 2:20

**Spoken Script:**
"We did not just build this; we rigorously tested it.

We created NepClinBench, a 60-case gold-standard clinical evaluation suite reflecting real patient cases in Nepal. 

When tested against raw Gemma 4 without our scaffolding, the raw model had an 18.3% hallucination rate and failed half the time on negated symptoms. 

With Sanchai's 3-tier pipeline, we achieved 1.000 precision, which means zero hallucinations, 100% negation accuracy, and sub-5-millisecond deterministic speed. 

Symptoms that patients deny, like 'jwaro chhaina', are accurately excluded from active conditions."

---

### Slide 5: The Ecosystem & Emergency Care
- **Headline:** Complete Longitudinal Care
- **Key Features on Slide:**
  - SanchAI Assistant: Grounded EHR companion with allergy contraindication alerts
  - Emergency Health QR: Offline optical triage card for paramedics
  - Global Interoperability: HL7 FHIR R4 Bundle and printable Doctor Summary PDF
- **Speaker Timing:** 2:20 - 3:00

**Spoken Script:**
"Sanchai provides an end-to-end ecosystem:

SanchAI is our multimodal EHR assistant. It knows the patient's entire longitudinal history. When a patient uploads a prescription slip or asks about an antibiotic, SanchAI cross-references their allergies and sounds an immediate warning if there is a contraindication.

For ambulances, Sanchai generates high-contrast emergency QR cards. When paramedics scan an unconscious patient, they immediately see their blood group, life-threatening allergies, and chronic diseases in under one second.

And for hospitals, we generate valid HL7 FHIR R4 bundles and print-ready A4 doctor summaries.

Now, let us show you Sanchai working live."

---

# Part 2: Live Product Demonstration (2 Minutes)

### Phase 1: Intake Studio & Approval Gate (3:00 - 3:30)
- **Screen Action:**
  1. Navigate to `http://localhost:3000/intake`.
  2. Click the preset button: **"Prescription Slip (Nepali Brand & Dosing)"**.
  3. Point out the text: *"Tab Cetamol 500mg 1 TDS, खोकी छ तर ज्वरो छैन"*.
  4. Click **"Run Clinical Normalization"**.
- **What to Say:**
  "Here in the Intake Studio, let us load a handwritten doctor prescription slip. Notice the code-mixing: 'Tab Cetamol 500mg' and 'खोकी छ तर ज्वरो छैन' (cough is present, but fever is absent).

  Look at the extraction results: 
  Cetamol is recognized and automatically resolved to its generic entity: Paracetamol. 
  Cough is flagged as an active symptom. 
  And fever is correctly flagged as NEGATED with zero false positives. 

  Most importantly, notice this action button: 'Approve & Commit to Patient Record'. Nothing writes to the ledger until the clinician reviews and confirms."

---

### Phase 2: SanchAI Multimodal Assistant & Allergy Guardrail (3:30 - 4:15)
- **Screen Action:**
  1. Navigate to `http://localhost:3000/chatbot`.
  2. Show the patient selector set to **Ram Bahadur Shrestha**.
  3. Point out the live badges at the top: `B+`, `Allergy: Penicillin`, `Typhoid fever`.
  4. Click the suggested prompt chip: **"Can I take Amoxicillin or beta-lactam antibiotics with my allergy?"**.
  5. Click **"Send"**.
- **What to Say:**
  "Now let us consult SanchAI, our EHR-grounded clinical assistant. 

  SanchAI knows that Ram Bahadur has a severe, documented Penicillin allergy. 

  Let us ask SanchAI: 'Can I take Amoxicillin for my throat infection?' 

  Watch the instant safety alert trigger: 
  CRITICAL CONTRAINDICATION. Patient has a severe allergy to Penicillin. The drug Amoxicillin is a beta-lactam derivative and poses a severe risk of anaphylaxis.

  SanchAI can also ingest uploaded lab PDFs or camera photos, explain lab values in plain conversational Nepali, and generate pre-visit doctor briefings."

---

### Phase 3: Longitudinal Ledger & Emergency QR Scanner (4:15 - 5:00)
- **Screen Action:**
  1. Navigate to `http://localhost:3000/patients/patient_ram`.
  2. Show the clinical timeline encounters.
  3. Highlight the two action buttons: **"Download Doctor Summary PDF"** and **"View HL7 FHIR R4 Bundle"**.
  4. Navigate to `http://localhost:3000/scan`.
  5. Click the demo button: **"Scan Ram Bahadur (AK-NP-8841)"**.
  6. The screen decodes and opens `/emergency/[token]`.
- **What to Say:**
  "On the patient record page, doctors have complete longitudinal visibility across past visits. With one click, they can export a print-ready A4 doctor summary or generate an international HL7 FHIR R4 bundle.

  Finally, in an emergency, an ambulance paramedic opens our optical scanner at `/scan`. 
  
  They target the patient's QR code. In less than one second, the emergency card opens offline. The paramedic immediately sees: Blood group B positive, severe Penicillin allergy, active chronic conditions. A life is saved before they even reach the hospital door.

  And if internet connectivity drops on the road, Sanchai seamlessly continues running via our locally installed Gemma 4 offline edge model.

  Sanchai turns fragmented paper into longitudinal health agency for every citizen of Nepal. 

  Thank you. Sanchai hunuhunchha!"
