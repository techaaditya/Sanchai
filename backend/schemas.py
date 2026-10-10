"""Pydantic v2 schemas for Sanchai API contracts.

These models define data transfer contracts across ingestion, 3-tier normalization,
patient health records, clinical standards (FHIR/QR), and evaluation benchmarks.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


# ==============================================================================
# 1. Normalization & Lexicon Contracts
# ==============================================================================

class GenericRef(BaseModel):
    """Reference to active pharmaceutical ingredient / generic compound."""
    concept_id: str
    canonical_en: str
    canonical_np: str


class NormalizedConcept(BaseModel):
    """Normalized clinical finding, condition, symptom, or medication."""
    concept_id: str
    surface_form: str = Field(description="Exact span as it appeared in source text")
    canonical_en: str
    canonical_np: str
    concept_type: str = Field(description="condition | symptom | medication | anatomy | lab")
    tier: int = Field(ge=1, le=3, description="1: Exact, 2: Fuzzy/Orthography, 3: Gemma Constrained")
    confidence: float
    negated: bool = False
    start: int = Field(description="Start character index in prepared text")
    end: int = Field(description="End character index in prepared text")
    reasoning: str | None = None
    icd11_code: str | None = None
    icd10_code: str | None = None
    generic: GenericRef | None = None

    @classmethod
    def from_match(cls, match: Any, lexicon: Any) -> NormalizedConcept:
        concept = match.concept
        generic = lexicon.generic_for(concept) if hasattr(lexicon, "generic_for") else None
        return cls(
            concept_id=concept.concept_id,
            surface_form=match.surface_form,
            canonical_en=concept.canonical_en,
            canonical_np=concept.canonical_np,
            concept_type=concept.concept_type,
            tier=match.tier,
            confidence=match.confidence,
            negated=match.negated,
            start=match.start_char,
            end=match.end_char,
            reasoning=match.reasoning,
            icd11_code=concept.icd11_code,
            icd10_code=concept.icd10_code,
            generic=(
                GenericRef(
                    concept_id=generic.concept_id,
                    canonical_en=generic.canonical_en,
                    canonical_np=generic.canonical_np,
                )
                if generic
                else None
            ),
        )


class NormalizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    use_model: bool = Field(
        default=True,
        description="Whether Tier 3 model routing is allowed when unconstrained"
    )


class NormalizeResponse(BaseModel):
    text: str = ""
    prepared_text: str = ""
    concepts: list[NormalizedConcept] = Field(default_factory=list)
    modifiers: list[NormalizedConcept] = Field(
        default_factory=list,
        description="Body sites, durations, and negation markers"
    )
    duration_days: int | None = None
    frequency_per_day: int | None = None
    unmatched: list[str] = Field(default_factory=list)
    tier_counts: dict[int, int] = Field(default_factory=dict)

    @classmethod
    def from_result(cls, result: Any, lexicon: Any) -> NormalizeResponse:
        assertions = result.assertions
        return cls(
            text=result.text,
            prepared_text=result.prepared_text,
            concepts=[NormalizedConcept.from_match(m, lexicon) for m in assertions],
            modifiers=[NormalizedConcept.from_match(m, lexicon) for m in result.matches if m not in assertions],
            duration_days=result.duration_days,
            frequency_per_day=result.frequency_per_day,
            unmatched=result.unmatched,
            tier_counts=result.tier_counts(),
        )


class LexiconEntry(BaseModel):
    """Individual concept in the clinical lexicon."""
    concept_id: str
    canonical_en: str
    canonical_np: str
    concept_type: str
    preferred_register: str | None = None
    devanagari_aliases: list[str] = Field(default_factory=list)
    romanized_aliases: list[str] = Field(default_factory=list)
    latin_aliases: list[str] = Field(default_factory=list)
    generic_of: str | None = None
    icd11_code: str | None = None
    icd10_code: str | None = None
    negation_sensitive: bool = False
    duration_days: int | None = None
    frequency_per_day: int | None = None


class LexiconResponse(BaseModel):
    total: int
    counts_by_type: dict[str, int]
    license: str = "CC-BY-4.0"
    review_status: str = "clinician review pending"
    entries: list[LexiconEntry]


# ==============================================================================
# 2. Intake & Ingestion Pipeline Contracts
# ==============================================================================

class CorrectionOut(BaseModel):
    """Individual OCR or phonetic correction applied to transcript."""
    original: str
    replacement: str
    start: int
    end: int
    reason: str
    confidence: float


class InlineNote(BaseModel):
    """Warning or informational hint produced during pipeline execution."""
    level: str = Field(description="info | warning | error")
    message_np: str
    message_en: str


class IntakeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    use_model: bool = True
    correct: bool = Field(
        default=True,
        description="Run lexicon-constrained OCR/spelling correction"
    )


class IntakeResponse(BaseModel):
    raw_transcript: str = Field(description="Verbatim extraction from vision/document")
    corrected_text: str
    extraction_method: str = Field(
        description="pymupdf | gemma4_vlm | direct | unavailable"
    )
    extraction_status: str = Field(description="ok | engine_unavailable | empty | unsupported")
    input_type: str = Field(description="text | image | pdf")
    document_class: str = Field(description="prescription | lab_report | bill | note")
    document_class_evidence: list[str] = Field(default_factory=list)
    corrections: list[CorrectionOut] = Field(default_factory=list)
    unverified: list[str] = Field(default_factory=list)
    asset_path: str | None = None
    pages: int | None = None
    notes: list[InlineNote] = Field(default_factory=list)
    normalized: NormalizeResponse | None = None


# ==============================================================================
# 3. Patient & Record Timeline Contracts
# ==============================================================================

class Allergy(BaseModel):
    substance_en: str
    substance_np: str | None = None
    severity: str | None = None


class ConditionRef(BaseModel):
    concept_id: str
    canonical_en: str
    canonical_np: str
    icd11_code: str | None = None
    icd10_code: str | None = None


class PatientSummary(BaseModel):
    id: str
    name: str
    name_np: str | None = None
    sanchai_id: str = Field(default="SANCHAI-0001", description="A Sanchai patient identifier.")
    arogya_id: str | None = Field(default=None, description="Legacy identifier alias")
    age: int | None = None
    gender: str | None = None
    gender_np: str | None = None
    district: str | None = None
    blood_group: str | None = None
    entry_count: int = 0


class PatientDetail(PatientSummary):
    dob: str | None = None
    qr_token: str | None = None
    allergies: list[Allergy] = Field(default_factory=list)
    conditions: list[ConditionRef] = Field(default_factory=list)
    synthetic: bool = True


class RecordConcept(BaseModel):
    """Concept stored with a confirmed record entry."""
    concept_id: str
    canonical_en: str
    canonical_np: str
    concept_type: str
    negated: bool = False
    surface_form: str
    tier: int
    confidence: float
    start: int
    end: int
    reasoning: str | None = None
    icd11_code: str | None = None
    icd10_code: str | None = None
    generic: GenericRef | None = None


class RecordEntrySummary(BaseModel):
    id: str
    patient_id: str
    input_type: str
    document_class: str | None = None
    facility_name: str | None = None
    record_date: str = Field(description="Gregorian ISO-8601 (YYYY-MM-DD)")
    record_date_bs: str | None = Field(default=None, description="Bikram Sambat display string")
    extraction_method: str | None = None
    summary_np: str
    concept_count: int
    negated_count: int
    icd11_code: str | None = None
    icd10_code: str | None = None
    icd_link_status: str | None = None
    has_asset: bool = False
    tiers: list[int] = Field(default_factory=list)


class RecordEntryDetail(RecordEntrySummary):
    raw_transcript: str | None = None
    corrected_text: str | None = None
    asset_path: str | None = None
    meaning_np: str | None = None
    concepts: list[RecordConcept] = Field(default_factory=list)
    modifiers: list[RecordConcept] = Field(default_factory=list)
    duration_days: int | None = None
    frequency_per_day: int | None = None
    unmatched: list[str] = Field(default_factory=list)
    notes: list[InlineNote] = Field(default_factory=list)
    dangling_concept_ids: list[str] = Field(default_factory=list)


class CommitEntryRequest(BaseModel):
    """Approval-Before-Write gate request model."""
    input_type: str = Field(description="text | image | pdf")
    record_date: str = Field(description="Gregorian ISO-8601 (YYYY-MM-DD)")
    normalized: NormalizeResponse
    document_class: str | None = None
    facility_name: str | None = None
    record_date_bs: str | None = None
    raw_transcript: str | None = None
    corrected_text: str | None = None
    extraction_method: str | None = None
    asset_path: str | None = None
    meaning_np: str | None = None
    notes: list[InlineNote] = Field(default_factory=list)


class RecordResponse(BaseModel):
    patient: PatientDetail
    entries: list[RecordEntrySummary]


# ==============================================================================
# 4. Standards, Emergency QR & Evaluation Contracts
# ==============================================================================

class QrPayload(BaseModel):
    """Emergency responder payload encoded into QR."""
    sanchai_id: str = Field(default="SANCHAI-0001", description="A Sanchai patient identifier.")
    arogya_id: str | None = Field(default=None, description="Legacy identifier alias")
    qr_token: str
    name: str
    name_np: str | None = None
    blood_group: str | None = None
    allergies: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    synthetic: bool = True
    qr_png: str | None = None
    encodes: str | None = None


class FhirBundle(BaseModel):
    """HL7 FHIR R4 Collection Bundle strictly excluding negated concepts."""
    resourceType: str = "Bundle"
    type: str = "collection"
    entry: list[dict[str, Any]] = Field(default_factory=list)
    negated_excluded: int = 0
    synthetic: bool = True


class EvalCategoryMetrics(BaseModel):
    total: int
    exact_matches: int
    exact_match_rate: float
    precision: float
    recall: float
    f1: float


class EvalReport(BaseModel):
    """NepClinBench evaluation report structure."""
    total_samples: int
    exact_matches: int
    exact_match_rate: float
    overall_precision: float
    overall_recall: float
    overall_f1: float
    negation_accuracy: float
    latency_ms_per_item: float
    categories: dict[str, EvalCategoryMetrics] = Field(default_factory=dict)
    model_name: str = "lexicon_3tier"
    timestamp: str | None = None
