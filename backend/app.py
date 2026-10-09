from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.data_store import get_dashboard, get_entry_detail, get_patient_detail, get_patient_entries


class GenericRef(BaseModel):
    concept_id: str
    canonical_en: str
    canonical_np: str


class NormalizedConcept(BaseModel):
    concept_id: str
    surface_form: str
    canonical_en: str
    canonical_np: str
    concept_type: str
    tier: int = Field(ge=1, le=3)
    confidence: float
    negated: bool
    start: int
    end: int
    reasoning: str | None = None
    icd11_code: str | None = None
    icd10_code: str | None = None
    generic: GenericRef | None = None


class NormalizeResponse(BaseModel):
    text: str
    prepared_text: str
    concepts: list[NormalizedConcept]
    modifiers: list[NormalizedConcept] = Field(default_factory=list)
    duration_days: int | None = None
    frequency_per_day: int | None = None
    unmatched: list[str] = Field(default_factory=list)
    tier_counts: dict[str, int] = Field(default_factory=dict)


class InlineNote(BaseModel):
    level: str
    message_np: str
    message_en: str


class IntakeResponse(BaseModel):
    raw_transcript: str
    corrected_text: str
    extraction_method: str
    extraction_status: str
    input_type: str
    document_class: str
    document_class_evidence: list[str]
    corrections: list[dict[str, Any]] = Field(default_factory=list)
    unverified: list[str] = Field(default_factory=list)
    asset_path: str | None = None
    pages: int | None = None
    notes: list[InlineNote] = Field(default_factory=list)
    normalized: NormalizeResponse | None = None


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


class PatientDetail(BaseModel):
    id: str
    name: str
    name_np: str | None = None
    sanchai_id: str
    arogya_id: str | None = None
    age: int | None = None
    gender: str | None = None
    gender_np: str | None = None
    district: str | None = None
    blood_group: str | None = None
    entry_count: int = 0
    dob: str | None = None
    qr_token: str | None = None
    allergies: list[Allergy] = Field(default_factory=list)
    conditions: list[ConditionRef] = Field(default_factory=list)
    synthetic: bool = True


class RecordConcept(BaseModel):
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
    label: str
    status: str
    document_class: str | None = None
    facility_name: str | None = None
    record_date: str
    record_date_bs: str | None = None
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
    normalized: NormalizeResponse | None = None


class DashboardResponse(BaseModel):
    patient: PatientDetail
    entries: list[RecordEntrySummary]
    intake: IntakeResponse


app = FastAPI(title="Sanchai API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "sanchai-api", "status": "ok"}


@app.get("/api/v1/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "backend": settings.resolved_backend,
        "model": settings.active_model_name,
        "supported_modalities": ["image", "pdf", "text"],
    }


@app.get("/api/v1/dashboard", response_model=DashboardResponse)
def dashboard() -> dict[str, Any]:
    return get_dashboard()


@app.get("/api/v1/patients/{patient_id}", response_model=PatientDetail)
def patient_detail(patient_id: str) -> dict[str, Any]:
    patient = get_patient_detail(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.get("/api/v1/patients/{patient_id}/entries", response_model=list[RecordEntrySummary])
def patient_entries(patient_id: str) -> list[dict[str, Any]]:
    return get_patient_entries(patient_id)


@app.get("/api/v1/entries/{entry_id}", response_model=RecordEntryDetail)
def entry_detail(entry_id: str) -> dict[str, Any]:
    entry = get_entry_detail(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry