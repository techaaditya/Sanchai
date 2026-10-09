from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PRIMARY_PATIENT_ID = "patient-001"
PRIMARY_PATIENT_SOURCE_ID = "patient_ram"

ENTRY_ALIASES = {
    "entry-1024": "entry_rx_typhoid_01",
    "entry-1023": "entry_lab_01",
    "entry-1022": "entry_voice_negation_01",
}

COMMITTED_ENTRY_IDS: set[str] = set()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_patients() -> list[dict[str, Any]]:
    data = _load_json(DATA_DIR / "seed_patients.json")
    return data if isinstance(data, list) else []


@lru_cache(maxsize=1)
def load_entries() -> list[dict[str, Any]]:
    data = _load_json(DATA_DIR / "seed_entries.json")
    return data if isinstance(data, list) else []


@lru_cache(maxsize=1)
def load_lexicon() -> dict[str, dict[str, Any]]:
    raw = _load_json(DATA_DIR / "nepali_clinical_lexicon.json")
    concepts = raw if isinstance(raw, list) else raw.get("concepts", [])
    index: dict[str, dict[str, Any]] = {}
    for item in concepts:
        concept_id = item.get("concept_id")
        if isinstance(concept_id, str):
            index[concept_id] = item
    return index


def _resolve_patient_source_id(patient_id: str) -> str | None:
    if patient_id in {PRIMARY_PATIENT_ID, PRIMARY_PATIENT_SOURCE_ID}:
        return PRIMARY_PATIENT_SOURCE_ID
    return None


def _resolve_entry_source_id(entry_id: str) -> str | None:
    if entry_id in ENTRY_ALIASES:
        return ENTRY_ALIASES[entry_id]
    if entry_id in ENTRY_ALIASES.values():
        return entry_id
    return None


def _concept_lookup(concept_id: str) -> dict[str, Any] | None:
    return load_lexicon().get(concept_id)


def _concept_ref(concept_id: str) -> dict[str, Any] | None:
    concept = _concept_lookup(concept_id)
    if not concept:
        return None
    return {
        "concept_id": concept_id,
        "canonical_en": concept.get("canonical_en", concept_id),
        "canonical_np": concept.get("canonical_np", concept.get("canonical_en", concept_id)),
        "icd11_code": concept.get("icd11_code"),
        "icd10_code": concept.get("icd10_code"),
    }


def _concept_out(concept_id: str, *, negated: bool = False) -> dict[str, Any] | None:
    concept = _concept_lookup(concept_id)
    if not concept:
        return None

    canonical_en = str(concept.get("canonical_en", concept_id))
    canonical_np = str(concept.get("canonical_np", canonical_en))
    generic_of = concept.get("generic_of")
    generic = _concept_ref(str(generic_of)) if isinstance(generic_of, str) and generic_of else None

    return {
        "concept_id": concept_id,
        "surface_form": canonical_np,
        "canonical_en": canonical_en,
        "canonical_np": canonical_np,
        "concept_type": str(concept.get("concept_type", "condition")),
        "tier": 1,
        "confidence": 1.0,
        "negated": negated,
        "start": 0,
        "end": len(canonical_np),
        "reasoning": None,
        "icd11_code": concept.get("icd11_code"),
        "icd10_code": concept.get("icd10_code"),
        "generic": generic,
    }


def _seed_patient() -> dict[str, Any]:
    for patient in load_patients():
        if patient.get("id") == PRIMARY_PATIENT_SOURCE_ID:
            return patient
    return load_patients()[0] if load_patients() else {}


def _seed_entry(source_id: str) -> dict[str, Any] | None:
    for entry in load_entries():
        if entry.get("id") == source_id:
            return entry
    return None


def _build_patient_detail() -> dict[str, Any]:
    patient = _seed_patient()
    entry_ids = [ENTRY_ALIASES["entry-1024"], ENTRY_ALIASES["entry-1023"], ENTRY_ALIASES["entry-1022"]]
    conditions: dict[str, dict[str, Any]] = {}

    for source_id in entry_ids:
        entry = _seed_entry(source_id)
        if not entry:
            continue
        for concept_id in entry.get("concepts", []):
            concept = _concept_lookup(str(concept_id))
            if not concept or concept.get("concept_type") != "condition":
                continue
            conditions.setdefault(str(concept_id), _concept_ref(str(concept_id)) or {})
        for concept_id in entry.get("negated_concepts", []):
            conditions.pop(str(concept_id), None)

    return {
        "id": PRIMARY_PATIENT_ID,
        "name": patient.get("name", "Demo Patient"),
        "name_np": patient.get("name_np"),
        "sanchai_id": "SANCHAI-0001",
        "arogya_id": patient.get("arogya_id"),
        "age": patient.get("age"),
        "gender": patient.get("gender"),
        "gender_np": patient.get("gender_np"),
        "district": patient.get("district"),
        "blood_group": patient.get("blood_group"),
        "entry_count": 3,
        "dob": patient.get("dob"),
        "qr_token": "tok_patient_001",
        "allergies": patient.get("allergies", []),
        "conditions": list(conditions.values()),
        "synthetic": bool(patient.get("synthetic", True)),
    }


def _build_timeline_entry(summary_id: str, source_entry: dict[str, Any], *, label: str, status: str, input_type: str) -> dict[str, Any]:
    concepts = source_entry.get("concepts", [])
    negated = set(str(item) for item in source_entry.get("negated_concepts", []))
    mapped_concepts = [
        concept
        for concept in (
            _concept_out(str(concept_id), negated=str(concept_id) in negated)
            for concept_id in concepts
        )
        if concept is not None
    ]

    normalized = {
        "text": str(source_entry.get("raw_transcript", "")),
        "prepared_text": str(source_entry.get("raw_transcript", "")),
        "concepts": mapped_concepts,
        "modifiers": [],
        "duration_days": None,
        "frequency_per_day": None,
        "unmatched": [],
        "tier_counts": {"1": len(mapped_concepts), "2": 0, "3": 0},
    }

    summary_np = str(source_entry.get("meaning_np") or source_entry.get("raw_transcript", ""))
    if summary_id == "entry-1023":
        summary_np = "CBC रिपोर्ट PDF बाट प्रत्यक्ष निकालिएको छ।"
    elif summary_id == "entry-1022":
        summary_np = "ज्वरो छैन तर खोकी छ।"

    return {
        "id": summary_id,
        "patient_id": PRIMARY_PATIENT_ID,
        "input_type": input_type,
        "label": label,
        "status": status,
        "document_class": source_entry.get("document_class"),
        "facility_name": source_entry.get("facility_name"),
        "record_date": source_entry.get("record_date"),
        "record_date_bs": source_entry.get("record_date_bs"),
        "extraction_method": "gemma4_vlm" if summary_id == "entry-1024" else ("pymupdf" if summary_id == "entry-1023" else "direct"),
        "summary_np": summary_np,
        "concept_count": len(mapped_concepts),
        "negated_count": sum(1 for concept in mapped_concepts if concept["negated"]),
        "icd11_code": source_entry.get("icd11_code"),
        "icd10_code": source_entry.get("icd10_code"),
        "icd_link_status": source_entry.get("icd_link_status"),
        "has_asset": bool(source_entry.get("asset_path")),
        "tiers": [1] if summary_id == "entry-1023" else [1, 2],
        "raw_transcript": source_entry.get("raw_transcript"),
        "corrected_text": source_entry.get("raw_transcript"),
        "asset_path": source_entry.get("asset_path"),
        "meaning_np": source_entry.get("meaning_np"),
        "concepts": mapped_concepts,
        "modifiers": [],
        "duration_days": None,
        "frequency_per_day": None,
        "unmatched": [],
        "notes": [{
            "level": "info",
            "message_np": "डेमो डाटा बाट लोड गरिएको",
            "message_en": "Loaded from seeded demo data",
        }],
        "dangling_concept_ids": [],
        "normalized": normalized,
    }


def get_patient_detail(patient_id: str) -> dict[str, Any] | None:
    if _resolve_patient_source_id(patient_id) is None:
        return None
    return _build_patient_detail()


def get_patient_entries(patient_id: str) -> list[dict[str, Any]]:
    if _resolve_patient_source_id(patient_id) is None:
        return []

    rx = _seed_entry(ENTRY_ALIASES["entry-1024"])
    lab = _seed_entry(ENTRY_ALIASES["entry-1023"])
    note = _seed_entry(ENTRY_ALIASES["entry-1022"])

    entries: list[dict[str, Any]] = []
    if rx:
        entries.append(
            _build_timeline_entry(
                "entry-1024",
                rx,
                label="Handwritten prescription",
                status="committed" if "entry-1024" in COMMITTED_ENTRY_IDS else "review",
                input_type="image",
            )
        )
    if lab:
        entries.append(_build_timeline_entry("entry-1023", lab, label="Digital lab report", status="committed", input_type="pdf"))
    if note:
        entries.append(_build_timeline_entry("entry-1022", note, label="Clinic note", status="committed", input_type="text"))

    return entries


def get_entry_detail(entry_id: str) -> dict[str, Any] | None:
    source_id = _resolve_entry_source_id(entry_id)
    if source_id is None:
        return None

    source_entry = _seed_entry(source_id)
    if not source_entry:
        return None

    status = "committed" if entry_id in COMMITTED_ENTRY_IDS else ("review" if entry_id == "entry-1024" else "committed")

    if entry_id == "entry-1024":
        return _build_timeline_entry("entry-1024", source_entry, label="Handwritten prescription", status=status, input_type="image")
    if entry_id == "entry-1023":
        return _build_timeline_entry("entry-1023", source_entry, label="Digital lab report", status="committed", input_type="pdf")
    return _build_timeline_entry("entry-1022", source_entry, label="Clinic note", status="committed", input_type="text")


def commit_entry(entry_id: str) -> dict[str, Any] | None:
    entry = get_entry_detail(entry_id)
    if not entry:
        return None

    COMMITTED_ENTRY_IDS.add(entry_id)
    committed = dict(entry)
    committed["status"] = "committed"
    return committed


def get_dashboard() -> dict[str, Any]:
    patient = get_patient_detail(PRIMARY_PATIENT_ID)
    entries = get_patient_entries(PRIMARY_PATIENT_ID)
    intake = get_entry_detail("entry-1024")

    return {
        "patient": patient,
        "entries": entries,
        "intake": {
            "raw_transcript": intake.get("raw_transcript") if intake else "",
            "corrected_text": intake.get("corrected_text") if intake else "",
            "extraction_method": intake.get("extraction_method") if intake else "gemma4_vlm",
            "extraction_status": "ok",
            "input_type": "image",
            "document_class": "prescription",
            "document_class_evidence": ["handwritten medication names", "prescription layout"],
            "corrections": [],
            "unverified": [],
            "asset_path": intake.get("asset_path") if intake else None,
            "pages": 1,
            "notes": intake.get("notes") if intake else [],
            "normalized": intake.get("normalized") if intake else None,
        },
    }