import type {
  IntakeResponse,
  PatientDetail,
  RecordEntryDetail,
  RecordEntrySummary,
  NormalizeResponse
} from "@/lib/contracts";

const normalizedPreview: NormalizeResponse = {
  text: "ज्वरो छैन, खोकी छ, सिटामोल ५०० एमजी",
  prepared_text: "ज्वरो छैन खोकी छ सिटामोल 500 एमजी",
  concepts: [
    {
      concept_id: "NCL-0101",
      surface_form: "ज्वरो",
      canonical_en: "Fever",
      canonical_np: "ज्वरो",
      concept_type: "condition",
      tier: 1,
      confidence: 1,
      negated: true,
      start: 0,
      end: 5
    },
    {
      concept_id: "NCL-0184",
      surface_form: "खोकी",
      canonical_en: "Cough",
      canonical_np: "खोकी",
      concept_type: "symptom",
      tier: 1,
      confidence: 1,
      negated: false,
      start: 7,
      end: 11
    },
    {
      concept_id: "NCL-0229",
      surface_form: "सिटामोल",
      canonical_en: "Paracetamol",
      canonical_np: "प्यारासिटामोल",
      concept_type: "drug_brand",
      tier: 2,
      confidence: 0.95,
      negated: false,
      start: 14,
      end: 21,
      generic: {
        concept_id: "NCL-0230",
        canonical_en: "Paracetamol",
        canonical_np: "प्यारासिटामोल"
      }
    }
  ],
  modifiers: [],
  duration_days: 2,
  frequency_per_day: 3,
  unmatched: [],
  tier_counts: {
    "1": 2,
    "2": 1,
    "3": 0
  }
};

const patient: PatientDetail = {
  id: "patient-001",
  name: "Demo Patient",
  name_np: "डेमो बिरामी",
  sanchai_id: "SANCHAI-0001",
  arogya_id: "AROGYA-1024",
  age: 34,
  gender: "female",
  gender_np: "महिला",
  district: "Kathmandu",
  blood_group: "O+",
  entry_count: 3,
  dob: "1992-03-14",
  qr_token: "tok_demo_1024",
  allergies: [
    {
      substance_en: "Penicillin",
      substance_np: "पेनिसिलिन",
      severity: "high"
    }
  ],
  conditions: [
    {
      concept_id: "NCL-0101",
      canonical_en: "Fever",
      canonical_np: "ज्वरो",
      icd11_code: "MG26"
    }
  ],
  synthetic: true
};

const entries: RecordEntryDetail[] = [
  {
    id: "entry-1024",
    patient_id: patient.id,
    input_type: "image",
    label: "Handwritten prescription",
    status: "review",
    document_class: "prescription",
    facility_name: "Demo Clinic",
    record_date: "2026-10-09",
    record_date_bs: "2083-06-23",
    extraction_method: "gemma4_vlm",
    summary_np: "ज्वरो छैन, खोकी छ। सिटामोल ५०० एमजी लेखिएको छ।",
    concept_count: 3,
    negated_count: 1,
    icd_link_status: "partial",
    has_asset: true,
    tiers: [1, 2],
    raw_transcript: normalizedPreview.text,
    corrected_text: normalizedPreview.prepared_text,
    concepts: normalizedPreview.concepts.map((concept) => ({
      concept_id: concept.concept_id,
      canonical_en: concept.canonical_en,
      canonical_np: concept.canonical_np,
      concept_type: concept.concept_type,
      negated: concept.negated,
      surface_form: concept.surface_form,
      tier: concept.tier,
      confidence: concept.confidence,
      start: concept.start,
      end: concept.end,
      generic: concept.generic ?? null
    })),
    notes: [
      {
        level: "info",
        message_np: "नकारात्मक ज्वरो सुरक्षित रूपमा चिह्नित गरिएको छ।",
        message_en: "Fever has been flagged as negated."
      }
    ],
    normalized: normalizedPreview
  },
  {
    id: "entry-1023",
    patient_id: patient.id,
    input_type: "pdf",
    label: "Digital lab report",
    status: "committed",
    document_class: "lab_report",
    facility_name: "City Lab",
    record_date: "2026-10-08",
    record_date_bs: "2083-06-22",
    extraction_method: "pymupdf",
    summary_np: "CBC रिपोर्ट PDF बाट प्रत्यक्ष निकालिएको छ।",
    concept_count: 1,
    negated_count: 0,
    icd_link_status: "linked",
    has_asset: true,
    tiers: [1],
    raw_transcript: "CBC within expected range.",
    corrected_text: "CBC within expected range.",
    concepts: [],
    notes: [],
    normalized: null
  },
  {
    id: "entry-1022",
    patient_id: patient.id,
    input_type: "text",
    label: "Clinic note",
    status: "committed",
    document_class: "note",
    facility_name: "Outpatient Desk",
    record_date: "2026-10-05",
    record_date_bs: "2083-06-19",
    extraction_method: "direct",
    summary_np: "Romanized note snapped to Nepali clinical concepts and duration.",
    concept_count: 2,
    negated_count: 0,
    icd_link_status: "unlinked",
    has_asset: false,
    tiers: [1, 2],
    raw_transcript: "jworo cha 3 din dekhi",
    corrected_text: "ज्वरो छ ३ दिन देखि",
    concepts: [],
    notes: [],
    normalized: null
  }
];

const intake: IntakeResponse = {
  raw_transcript: normalizedPreview.text,
  corrected_text: normalizedPreview.prepared_text,
  extraction_method: "gemma4_vlm",
  extraction_status: "ok",
  input_type: "image",
  document_class: "prescription",
  document_class_evidence: ["handwritten medication names", "prescription layout"],
  corrections: [],
  unverified: [],
  asset_path: "/uploads/demo-prescription.jpg",
  pages: 1,
  notes: normalizedPreview.concepts.length > 0 ? [{ level: "info", message_np: "प्राथमिक निष्कर्ष तयार छ।", message_en: "Primary extraction is ready." }] : [],
  normalized: normalizedPreview
};

export async function getPatientOverview() {
  return {
    patient,
    entries,
    intake
  };
}

export function getEmergencySummary() {
  return {
    patient,
    qrPayload: {
      sanchai_id: patient.sanchai_id,
      arogya_id: patient.arogya_id,
      qr_token: patient.qr_token,
      name: patient.name,
      name_np: patient.name_np,
      blood_group: patient.blood_group,
      allergies: patient.allergies.map((allergy) => allergy.substance_np ?? allergy.substance_en),
      conditions: patient.conditions.map((condition) => condition.canonical_np),
      synthetic: patient.synthetic,
      encodes: `sanchai://p/${patient.qr_token}`
    },
    highlights: [
      "Penicillin allergy",
      "Blood group O+",
      "Recent negated fever",
      "Prescription review status: ready"
    ]
  };
}

export function getIntakeStudio() {
  return {
    title: "Intake studio",
    sourceModes: ["image", "pdf", "text"],
    queue: [
      {
        id: "draft-901",
        title: "Handwritten prescription",
        subtitle: "OCR + normalization preview",
        status: "Ready for review",
      },
      {
        id: "draft-902",
        title: "Lab report PDF",
        subtitle: "Direct extraction path",
        status: "Queued",
      },
      {
        id: "draft-903",
        title: "Clinic note",
        subtitle: "Romanized text normalization",
        status: "Draft",
      },
    ],
    documentHints: [
      "Keep handwriting centered in the frame",
      "Preserve medication dosage and units",
      "Mark negation words clearly",
    ],
    preview: normalizedPreview,
  };
}

export function getScannerSession() {
  return {
    title: "QR scanner",
    lastScan: {
      token: patient.qr_token,
      patientName: patient.name_np,
      timestamp: "Today · 09:42",
      source: "Camera preview",
    },
    recentScans: [
      {
        token: "tok_demo_1024",
        label: "Demo emergency card",
        outcome: "Opened emergency summary",
      },
      {
        token: "tok_demo_5566",
        label: "Ward wristband",
        outcome: "Synthetic card matched",
      },
    ],
  };
}

export async function getPatientById(id: string) {
  const overview = await getPatientOverview();
  if (overview.patient.id !== id) {
    return null;
  }
  return overview.patient;
}

export async function getEntryById(id: string) {
  const overview = await getPatientOverview();
  return overview.entries.find((entry) => entry.id === id) ?? null;
}

export function getTimelineEntries(): RecordEntrySummary[] {
  return entries.map(({ concepts, notes, normalized, raw_transcript, corrected_text, ...summary }) => summary);
}