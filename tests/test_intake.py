import io
import fitz
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_intake_text_direct(client):
    payload = {
        "text": "टाइफाइड ज्वरोको लागि प्यारासिटामोल ५०० एमजी दिनको दुई पटक",
        "use_model": False,
        "correct": True,
    }
    response = client.post("/api/v1/intake/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["input_type"] == "text"
    assert data["extraction_method"] == "direct"
    assert data["extraction_status"] == "ok"
    assert data["raw_transcript"] == payload["text"]
    assert data["normalized"] is not None
    concepts = data["normalized"]["concepts"]
    assert len(concepts) >= 2
    concept_ids = {c["concept_id"] for c in concepts}
    # Should find Fever (NCL-0001) or Typhoid (NCL-0058) and Paracetamol (NCL-0088)
    assert "NCL-0088" in concept_ids or "NCL-0001" in concept_ids or "NCL-0058" in concept_ids


def test_intake_normalize_direct(client):
    payload = {
        "text": "खोकी छ तर ज्वरो छैन",
        "use_model": False,
    }
    response = client.post("/api/v1/intake/normalize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "concepts" in data
    # Check negation detection on fever ("ज्वरो छैन")
    fever = next((c for c in data["concepts"] if c["concept_id"] == "NCL-0001"), None)
    if fever:
        assert fever["negated"] is True


def test_intake_pdf_digital(client):
    # Create an in-memory digital PDF with PyMuPDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        fitz.Point(50, 72),
        "Rx: Tab Paracetamol 500mg bd. Patient reports high fever and cough. Follow up in 3 days.",
    )
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("prescription_test.pdf", pdf_bytes, "application/pdf")}
    data = {"use_model": "false", "correct": "true"}

    response = client.post("/api/v1/intake/ocr", files=files, data=data)
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["input_type"] == "pdf"
    assert resp_data["extraction_method"] == "pymupdf"
    assert resp_data["extraction_status"] == "ok"
    assert resp_data["document_class"] == "prescription"
    assert resp_data["normalized"] is not None
    assert len(resp_data["normalized"]["concepts"]) >= 1


def test_intake_image_offline_resilience(client):
    # Dummy PNG bytes
    dummy_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
        b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("rx_test.png", dummy_png, "image/png")}
    data = {"use_model": "true", "correct": "true"}

    # Must degrade gracefully without 500 error even if cloud Ollama is offline
    response = client.post("/api/v1/intake/ocr", files=files, data=data)
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["input_type"] == "image"
    assert resp_data["extraction_status"] in {"ok", "engine_unavailable"}
    if resp_data["extraction_status"] == "engine_unavailable":
        assert len(resp_data["notes"]) >= 1


def test_intake_stream(client):
    form_data = {
        "text": "ज्वरो आएको छ",
        "use_model": "false",
        "correct": "true",
    }
    response = client.post("/api/v1/intake/stream", data=form_data)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "event: routing" in content
    assert "event: done" in content
