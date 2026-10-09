from __future__ import annotations

from typing import Any, Iterable, Sequence

from backend.record.entries import StoredNormalization
from backend.schemas import FhirBundle

SYSTEM_ICD11 = "http://id.who.int/icd/release/11/mms"
SYSTEM_ICD10 = "http://hl7.org/fhir/sid/icd-10"
SYSTEM_LEXICON = "urn:sanchai:nepali-clinical-lexicon"

RESOURCE_FOR_TYPE = {
    "condition": "Condition",
    "symptom": "Condition",
    "investigation": "Observation",
    "drug_generic": "MedicationRequest",
    "drug_brand": "MedicationRequest",
}


def _codeable(concept: Any) -> dict[str, Any]:
    codings: list[dict[str, str]] = [
        {
            "system": SYSTEM_LEXICON,
            "code": concept.concept_id,
            "display": concept.canonical_en,
        }
    ]
    if concept.icd11_code:
        codings.append(
            {"system": SYSTEM_ICD11, "code": concept.icd11_code, "display": concept.canonical_en}
        )
    if concept.icd10_code:
        codings.append(
            {"system": SYSTEM_ICD10, "code": concept.icd10_code, "display": concept.canonical_en}
        )
    return {"coding": codings, "text": concept.canonical_np}


def _patient_resource(patient: Any) -> dict[str, Any]:
    sanchai_id = patient["sanchai_id"] or patient["arogya_id"] or f"SANCHAI-{patient['id']}"
    identifiers = [
        {
            "system": "urn:sanchai:patient-id",
            "value": sanchai_id,
        }
    ]
    if patient["arogya_id"]:
        identifiers.append(
            {
                "system": "urn:sanchai:legacy-arogya-id",
                "value": patient["arogya_id"],
            }
        )

    resource: dict[str, Any] = {
        "resourceType": "Patient",
        "id": patient["id"],
        "identifier": identifiers,
        "name": [{"text": patient["name_np"] or patient["name"]}],
    }
    if patient["gender"]:
        resource["gender"] = patient["gender"]
    if patient["dob"]:
        resource["birthDate"] = patient["dob"]
    return resource


def _allergy_resources(patient_id: str, allergies: Sequence[Any]) -> list[dict[str, Any]]:
    return [
        {
            "resourceType": "AllergyIntolerance",
            "id": row["id"],
            "patient": {"reference": f"Patient/{patient_id}"},
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active",
                    }
                ]
            },
            "code": {
                "coding": [
                    {
                        "display": row["substance_en"],
                    }
                ],
                "text": f"{row['substance_en']} ({row['substance_np']})" if row["substance_np"] else row["substance_en"],
            },
            **({"criticality": "high"} if row["severity"] == "severe" else {}),
        }
        for row in allergies
    ]


def _clinical_resources(
    patient_id: str, row: Any, normalization: StoredNormalization
) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    reference = {"reference": f"Patient/{patient_id}"}

    for index, item in enumerate(normalization.concepts):
        # Strict clinical safety rule: negated findings are never emitted as condition resources!
        if item.negated:
            continue

        resource_type = RESOURCE_FOR_TYPE.get(item.concept.concept_type)
        if resource_type is None:
            continue

        base: dict[str, Any] = {
            "resourceType": resource_type,
            "id": f"{row['id']}-{index}",
            "subject": reference,
        }

        if resource_type == "Condition":
            base["code"] = _codeable(item.concept)
            base["recordedDate"] = row["record_date"]
            base["verificationStatus"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "unconfirmed",
                    }
                ]
            }
        elif resource_type == "Observation":
            base["code"] = _codeable(item.concept)
            base["effectiveDateTime"] = row["record_date"]
            base["status"] = "registered"
        else:
            base["medicationCodeableConcept"] = _codeable(item.concept)
            base["authoredOn"] = row["record_date"]
            base["status"] = "unknown"
            base["intent"] = "order"
            if normalization.duration_days or normalization.frequency_per_day:
                timing: dict[str, Any] = {}
                if normalization.frequency_per_day:
                    timing["frequency"] = normalization.frequency_per_day
                    timing["period"] = 1
                    timing["periodUnit"] = "d"
                if normalization.duration_days:
                    timing["duration"] = normalization.duration_days
                    timing["durationUnit"] = "d"
                base["dosageInstruction"] = [{"timing": {"repeat": timing}}]

        resources.append(base)

    return resources


def build_bundle(
    patient: Any,
    allergies: Sequence[Any],
    entries: Iterable[tuple[Any, StoredNormalization]],
) -> FhirBundle:
    """Assemble HL7 FHIR R4 Collection Bundle strictly excluding negated concepts."""
    resources: list[dict[str, Any]] = [_patient_resource(patient)]
    resources.extend(_allergy_resources(patient["id"], allergies))

    excluded = 0
    for row, normalization in entries:
        excluded += sum(1 for item in normalization.concepts if item.negated)
        resources.extend(_clinical_resources(patient["id"], row, normalization))

    return FhirBundle(
        resourceType="Bundle",
        type="collection",
        entry=[{"resource": r} for r in resources],
        negated_excluded=excluded,
        synthetic=True,
    )
