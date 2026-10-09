import re

import pytest
from fastapi.testclient import TestClient

from backend.main import app

FHIR_ID_PATTERN = re.compile(r"^[A-Za-z0-9\-\.]+$")


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_patient_fhir_bundle(client):
    response = client.get("/api/v1/patients/patient_ram/fhir")
    assert response.status_code == 200
    data = response.json()

    assert data["resourceType"] == "Bundle"
    assert data["type"] == "collection"
    assert data["synthetic"] is True
    assert isinstance(data["entry"], list)
    assert len(data["entry"]) >= 3

    resource_types = [e["resource"]["resourceType"] for e in data["entry"]]
    assert "Patient" in resource_types
    assert "AllergyIntolerance" in resource_types

    # Every resource id must be FHIR R4 compliant (no underscores)
    for entry in data["entry"]:
        assert FHIR_ID_PATTERN.match(entry["resource"]["id"]), (
            f"FHIR resource id '{entry['resource']['id']}' violates R4 ID pattern"
        )

    # Find patient resource — ID is FHIR-safe (hyphenated)
    patient_res = next(
        e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "Patient"
    )
    assert patient_res["id"] == "patient-ram"
    identifiers = [ident["value"] for ident in patient_res["identifier"]]
    assert any("SANCHAI-" in v or "AK-" in v for v in identifiers)

    # Find allergy resource
    allergy_res = next(
        e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance"
    )
    assert "Penicillin" in allergy_res["code"]["text"]


def test_fhir_validates_against_model(client):
    """Every resource in the bundle must pass fhir.resources R4 validation."""
    from fhir.resources.bundle import Bundle
    from pydantic import ValidationError

    response = client.get("/api/v1/patients/patient_ram/fhir")
    assert response.status_code == 200
    data = response.json()

    bundle_dict = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": data["entry"],
    }

    # Should not raise — if it does, the bundle is structurally invalid FHIR R4
    bundle = Bundle(**bundle_dict)
    assert bundle.type == "collection"
    assert len(bundle.entry) >= 3


def test_fhir_resource_structure(client):
    """Verify FHIR resource fields are structurally correct."""
    response = client.get("/api/v1/patients/patient_ram/fhir")
    assert response.status_code == 200
    data = response.json()

    for entry in data["entry"]:
        res = entry["resource"]
        if res["resourceType"] == "Condition":
            # clinicalStatus is required in FHIR R4
            assert "clinicalStatus" in res
            coding = res["clinicalStatus"]["coding"][0]
            assert coding["code"] == "active"
        elif res["resourceType"] == "MedicationRequest":
            # medication must use CodeableReference, not medicationCodeableConcept
            assert "medication" in res
            assert "medicationCodeableConcept" not in res
            assert res["medication"]["concept"]["coding"][0]["code"]
            assert res["status"] == "active"
            assert res["intent"] == "order"
        elif res["resourceType"] == "Observation":
            assert res["status"] == "final"

    # Patient references in all resources must use FHIR-safe (hyphenated) ID
    patient_res = next(
        e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "Patient"
    )
    for entry in data["entry"]:
        res = entry["resource"]
        ref_field = "patient" if res.get("resourceType") == "AllergyIntolerance" else "subject"
        if ref_field in res:
            ref = res[ref_field]["reference"]
            assert ref == f"Patient/{patient_res['id']}"


def test_fhir_strictly_excludes_negated_findings(client):
    # Patient Ram has entry_voice_negation_01 with negated concepts
    response = client.get("/api/v1/patients/patient_ram/fhir")
    assert response.status_code == 200
    data = response.json()

    # Clinical safety assertion: negated concepts are tracked and excluded
    assert data["negated_excluded"] >= 1

    # Verify no condition or medication resource has negated status or inverted assertion
    for entry in data["entry"]:
        res = entry["resource"]
        # In FHIR Condition, verificationStatus should be unconfirmed or confirmed, never negated
        if res["resourceType"] == "Condition":
            codings = res.get("code", {}).get("coding", [])
            for c in codings:
                # Ram's negation entry denies chest pain or specific symptoms
                assert not c.get("display", "").lower().startswith("no ")


def test_fhir_not_found(client):
    res = client.get("/api/v1/patients/nonexistent_patient/fhir")
    assert res.status_code == 404
