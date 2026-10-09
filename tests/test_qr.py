import pytest
from fastapi.testclient import TestClient
from backend.main import app

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_patient_qr_json(client):
    response = client.get("/api/v1/patients/patient_ram/qr")
    assert response.status_code == 200
    data = response.json()
    assert data["sanchai_id"].startswith("SANCHAI-")
    assert data["qr_token"]
    assert data["encodes"] == f"sanchai://p/{data['qr_token']}"
    assert data["qr_png"].startswith("data:image/png;base64,")
    assert any("Penicillin" in a for a in data["allergies"])


def test_get_patient_qr_png_param(client):
    response = client.get("/api/v1/patients/patient_ram/qr?format=png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(PNG_MAGIC)


def test_get_patient_qr_image_route(client):
    response = client.get("/api/v1/patients/patient_ram/qr.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(PNG_MAGIC)


def test_get_qr_not_found(client):
    res = client.get("/api/v1/patients/nonexistent_patient/qr")
    assert res.status_code == 404
