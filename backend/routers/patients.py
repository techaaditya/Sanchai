from __future__ import annotations

import datetime as dt
import json
import sqlite3

from typing import Any
from fastapi import APIRouter, HTTPException, Query, Response

from backend.db import session
from backend.nlp.lexicon import Concept, Lexicon, get_lexicon
from backend.record import entries as record
from backend.record import qr
from backend.record.fhir import build_bundle
from backend.schemas import (
    Allergy,
    CommitEntryRequest,
    ConditionRef,
    FhirBundle,
    GenericRef,
    InlineNote,
    PatientDetail,
    PatientSummary,
    QrPayload,
    RecordConcept,
    RecordEntryDetail,
    RecordEntrySummary,
    RecordResponse,
)

router = APIRouter(tags=["record"])


def _age(dob: str | None, on: dt.date | None = None) -> int | None:
    if not dob:
        return None
    try:
        born = dt.date.fromisoformat(dob)
    except ValueError:
        return None
    today = on or dt.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _require_gregorian(value: str, field: str) -> str:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=f"{field} must be a Gregorian ISO date (YYYY-MM-DD)"
        ) from exc
    if not 1900 <= parsed.year <= dt.date.today().year + 1:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{field} year {parsed.year} is implausible for a Gregorian date — "
                "Bikram Sambat belongs in record_date_bs"
            ),
        )
    return value


def _to_record_concept(item: record.StoredConcept, lexicon: Lexicon) -> RecordConcept:
    generic = lexicon.generic_for(item.concept) if hasattr(lexicon, "generic_for") else None
    return RecordConcept(
        concept_id=item.concept.concept_id,
        canonical_en=item.concept.canonical_en,
        canonical_np=item.concept.canonical_np,
        concept_type=item.concept.concept_type,
        negated=item.negated,
        surface_form=item.surface_form or item.concept.canonical_np,
        tier=item.tier or 1,
        confidence=item.confidence or 1.0,
        start=item.start or 0,
        end=item.end or 0,
        reasoning=item.reasoning,
        icd11_code=item.concept.icd11_code,
        icd10_code=item.concept.icd10_code,
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


def _to_summary(row: sqlite3.Row, lexicon: Lexicon) -> RecordEntrySummary:
    norm = record.hydrate(row["normalized_json"], lexicon)
    tiers = sorted({c.tier for c in norm.all_concepts if c.tier is not None})
    return RecordEntrySummary(
        id=row["id"],
        patient_id=row["patient_id"],
        input_type=row["input_type"],
        document_class=row["document_class"],
        facility_name=row["facility_name"],
        record_date=row["record_date"],
        record_date_bs=row["record_date_bs"],
        extraction_method=row["extraction_method"],
        summary_np=record.summarize(norm),
        concept_count=len(norm.concepts),
        negated_count=sum(1 for c in norm.concepts if c.negated),
        icd11_code=row["icd11_code"],
        icd10_code=row["icd10_code"],
        icd_link_status=row["icd_link_status"],
        has_asset=bool(row["asset_path"]),
        tiers=tiers,
    )


def _to_detail(row: sqlite3.Row, lexicon: Lexicon) -> RecordEntryDetail:
    summary = _to_summary(row, lexicon)
    norm = record.hydrate(row["normalized_json"], lexicon)
    notes_raw = json.loads(row["notes_json"]) if row["notes_json"] else []
    notes = [InlineNote(**n) if isinstance(n, dict) else n for n in notes_raw]

    return RecordEntryDetail(
        **summary.model_dump(),
        raw_transcript=row["raw_transcript"],
        corrected_text=row["corrected_text"],
        asset_path=row["asset_path"],
        meaning_np=row["meaning_np"],
        concepts=[_to_record_concept(c, lexicon) for c in norm.concepts],
        modifiers=[_to_record_concept(c, lexicon) for c in norm.modifiers],
        duration_days=norm.duration_days,
        frequency_per_day=norm.frequency_per_day,
        unmatched=norm.unmatched,
        notes=notes,
        dangling_concept_ids=norm.dangling,
    )


def _build_patient_detail(patient: sqlite3.Row, con: sqlite3.Connection, lexicon: Lexicon) -> PatientDetail:
    allergies = [
        Allergy(
            substance_en=a["substance_en"],
            substance_np=a["substance_np"],
            severity=a["severity"],
        )
        for a in record.list_allergies(con, patient["id"])
    ]
    conditions = [
        ConditionRef(
            concept_id=c.concept_id,
            canonical_en=c.canonical_en,
            canonical_np=c.canonical_np,
            icd11_code=c.icd11_code,
            icd10_code=c.icd10_code,
        )
        for c in record.active_conditions(con, patient["id"], lexicon)
    ]
    entry_rows = record.list_entries(con, patient["id"])

    return PatientDetail(
        id=patient["id"],
        name=patient["name"],
        name_np=patient["name_np"],
        sanchai_id=patient["sanchai_id"] or patient["arogya_id"] or f"SANCHAI-{patient['id']}",
        arogya_id=patient["arogya_id"],
        age=_age(patient["dob"]),
        dob=patient["dob"],
        gender=patient["gender"],
        gender_np=patient["gender_np"],
        district=patient["district"],
        blood_group=patient["blood_group"],
        entry_count=len(entry_rows),
        qr_token=patient["qr_token"],
        allergies=allergies,
        conditions=conditions,
        synthetic=True,
    )


@router.get("/patients", response_model=list[PatientSummary])
def list_patients() -> list[PatientSummary]:
    with session() as con:
        rows = record.list_patients(con)
        result: list[PatientSummary] = []
        for p in rows:
            entry_count = len(record.list_entries(con, p["id"]))
            result.append(
                PatientSummary(
                    id=p["id"],
                    name=p["name"],
                    name_np=p["name_np"],
                    sanchai_id=p["sanchai_id"] or p["arogya_id"] or f"SANCHAI-{p['id']}",
                    arogya_id=p["arogya_id"],
                    age=_age(p["dob"]),
                    gender=p["gender"],
                    gender_np=p["gender_np"],
                    district=p["district"],
                    blood_group=p["blood_group"],
                    entry_count=entry_count,
                )
            )
        return result


@router.get("/patients/{patient_id}", response_model=PatientDetail)
def get_patient(patient_id: str) -> PatientDetail:
    lexicon = get_lexicon()
    with session() as con:
        p = record.get_patient(con, patient_id)
        if not p:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        return _build_patient_detail(p, con, lexicon)


@router.get("/patients/{patient_id}/record", response_model=RecordResponse)
def get_patient_record(
    patient_id: str,
    document_class: str | None = Query(default=None),
    query: str | None = Query(default=None),
) -> RecordResponse:
    lexicon = get_lexicon()
    with session() as con:
        p = record.get_patient(con, patient_id)
        if not p:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        patient_detail = _build_patient_detail(p, con, lexicon)
        entry_rows = record.list_entries(
            con, patient_id, document_class=document_class, query=query
        )
        entries = [_to_summary(row, lexicon) for row in entry_rows]
        return RecordResponse(patient=patient_detail, entries=entries)


@router.get("/patients/{patient_id}/entries/{entry_id}", response_model=RecordEntryDetail)
def get_entry(patient_id: str, entry_id: str) -> RecordEntryDetail:
    lexicon = get_lexicon()
    with session() as con:
        entry = record.get_entry(con, entry_id)
        if not entry or entry["patient_id"] != patient_id:
            raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found for patient")
        return _to_detail(entry, lexicon)


@router.post("/patients/{patient_id}/entries", response_model=RecordEntryDetail, status_code=201)
def commit_entry(patient_id: str, payload: CommitEntryRequest) -> RecordEntryDetail:
    """Approval-Before-Write gate: the only endpoint that mutates patient health records."""
    _require_gregorian(payload.record_date, "record_date")
    lexicon = get_lexicon()

    with session() as con:
        patient = record.get_patient(con, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

        entry_id = record.new_entry_id()

        # Find top ICD code from primary condition concepts if available
        icd11 = None
        icd10 = None
        for concept in payload.normalized.concepts:
            if concept.concept_type == "condition" and not concept.negated:
                if concept.icd11_code:
                    icd11 = concept.icd11_code
                if concept.icd10_code:
                    icd10 = concept.icd10_code
                if icd11:
                    break

        encoded_norm = record.encode_normalization(payload.normalized.model_dump())
        notes_json = (
            json.dumps([n.model_dump() for n in payload.notes], ensure_ascii=False)
            if payload.notes
            else None
        )

        row_data = {
            "id": entry_id,
            "patient_id": patient_id,
            "input_type": payload.input_type,
            "document_class": payload.document_class,
            "facility_name": payload.facility_name,
            "record_date": payload.record_date,
            "record_date_bs": payload.record_date_bs,
            "asset_path": payload.asset_path,
            "raw_transcript": payload.raw_transcript,
            "corrected_text": payload.corrected_text,
            "extraction_method": payload.extraction_method,
            "normalized_json": encoded_norm,
            "meaning_np": payload.meaning_np,
            "icd11_code": icd11,
            "icd10_code": icd10,
            "icd_link_status": "PENDING_LOCAL_WHO_VERIFICATION" if icd11 else None,
            "notes_json": notes_json,
        }

        record.insert_entry(con, row_data)
        created_row = record.get_entry(con, entry_id)
        assert created_row is not None
        return _to_detail(created_row, lexicon)


@router.get("/patients/{patient_id}/qr", response_model=QrPayload)
def get_patient_qr(
    patient_id: str,
    format: str | None = Query(default=None),
) -> Any:
    """Generate high-contrast Segno emergency QR payload and scannable code."""
    lexicon = get_lexicon()
    with session() as con:
        patient = record.get_patient(con, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

        qr_payload = qr.build_qr_payload(patient, con, lexicon)
        if format == "png":
            png_bytes = qr.encode_png_bytes(qr_payload.encodes or f"sanchai://p/{patient['qr_token']}")
            return Response(content=png_bytes, media_type="image/png")
        return qr_payload


@router.get("/patients/{patient_id}/qr.png")
def get_patient_qr_image(patient_id: str) -> Response:
    """Return scannable QR code PNG image bytes directly."""
    with session() as con:
        patient = record.get_patient(con, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        encodes = f"sanchai://p/{patient['qr_token']}"
        png_bytes = qr.encode_png_bytes(encodes)
        return Response(content=png_bytes, media_type="image/png")


@router.get("/patients/{patient_id}/fhir", response_model=FhirBundle)
def get_patient_fhir(patient_id: str) -> FhirBundle:
    """Generate HL7 FHIR R4 Collection Bundle strictly excluding negated findings."""
    lexicon = get_lexicon()
    with session() as con:
        patient = record.get_patient(con, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        allergies = record.list_allergies(con, patient_id)
        raw_entries = record.list_entries(con, patient_id)
        entries = [(row, record.hydrate(row["normalized_json"], lexicon)) for row in raw_entries]
        return build_bundle(patient, allergies, entries)
