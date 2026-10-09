export type IntakeMode = "image" | "pdf" | "text";

export type GenericRef = {
  concept_id: string;
  canonical_en: string;
  canonical_np: string;
};

export type NormalizedConcept = {
  concept_id: string;
  surface_form: string;
  canonical_en: string;
  canonical_np: string;
  concept_type: string;
  tier: 1 | 2 | 3;
  confidence: number;
  negated: boolean;
  start: number;
  end: number;
  reasoning?: string | null;
  icd11_code?: string | null;
  icd10_code?: string | null;
  generic?: GenericRef | null;
};

export type NormalizeResponse = {
  text: string;
  prepared_text: string;
  concepts: NormalizedConcept[];
  modifiers: NormalizedConcept[];
  duration_days?: number | null;
  frequency_per_day?: number | null;
  unmatched: string[];
  tier_counts: Record<string, number>;
};

export type CorrectionOut = {
  original: string;
  replacement: string;
  start: number;
  end: number;
  reason: string;
  confidence: number;
};

export type InlineNote = {
  level: "info" | "warning" | "error";
  message_np: string;
  message_en: string;
};

export type IntakeResponse = {
  raw_transcript: string;
  corrected_text: string;
  extraction_method: "pymupdf" | "gemma4_vlm" | "direct" | "unavailable";
  extraction_status: "ok" | "engine_unavailable" | "empty" | "unsupported";
  input_type: IntakeMode;
  document_class: "prescription" | "lab_report" | "bill" | "note";
  document_class_evidence: string[];
  corrections: CorrectionOut[];
  unverified: string[];
  asset_path?: string | null;
  pages?: number | null;
  notes: InlineNote[];
  normalized?: NormalizeResponse | null;
};

export type RecordConcept = {
  concept_id: string;
  canonical_en: string;
  canonical_np: string;
  concept_type: string;
  negated: boolean;
  surface_form: string;
  tier: number;
  confidence: number;
  start: number;
  end: number;
  reasoning?: string | null;
  icd11_code?: string | null;
  icd10_code?: string | null;
  generic?: GenericRef | null;
};

export type PatientSummary = {
  id: string;
  name: string;
  name_np?: string | null;
  sanchai_id: string;
  arogya_id?: string | null;
  age?: number | null;
  gender?: string | null;
  gender_np?: string | null;
  district?: string | null;
  blood_group?: string | null;
  entry_count: number;
};

export type PatientDetail = PatientSummary & {
  dob?: string | null;
  qr_token?: string | null;
  allergies: Array<{
    substance_en: string;
    substance_np?: string | null;
    severity?: string | null;
  }>;
  conditions: Array<{
    concept_id: string;
    canonical_en: string;
    canonical_np: string;
    icd11_code?: string | null;
    icd10_code?: string | null;
  }>;
  synthetic: boolean;
};

export type RecordEntrySummary = {
  id: string;
  patient_id: string;
  input_type: IntakeMode;
  label: string;
  status: "review" | "committed";
  document_class?: string | null;
  facility_name?: string | null;
  record_date: string;
  record_date_bs?: string | null;
  extraction_method?: string | null;
  summary_np: string;
  concept_count: number;
  negated_count: number;
  icd11_code?: string | null;
  icd10_code?: string | null;
  icd_link_status?: string | null;
  has_asset: boolean;
  tiers: number[];
};

export type RecordEntryDetail = RecordEntrySummary & {
  raw_transcript?: string | null;
  corrected_text?: string | null;
  concepts: RecordConcept[];
  notes: InlineNote[];
  normalized?: NormalizeResponse | null;
};