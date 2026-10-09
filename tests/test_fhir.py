import pytest
from fastapi.testclient import TestClient
from backend.main import app


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

    # Find patient resource
    patient_res = next(e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "Patient")
    assert patient_res["id"] == "patient_ram"
    identifiers = [ident["value"] for ident in patient_res["identifier"]]
    assert any("SANCHAI-" in v or "AK-" in v for v in identifiers)

    # Find allergy resource
    allergy_res = next(e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance")
    assert "Penicillin" in allergy_res["code"]["text"]


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
