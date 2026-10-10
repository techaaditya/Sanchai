"""Tests for SanchAI EHR Multimodal Assistant endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app




def test_chatbot_patients_list(client):
    response = client.get("/api/v1/chatbot/patients")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    ram = next((p for p in data if p["id"] == "patient_ram"), None)
    assert ram is not None
    assert ram["name"] == "Ram Bahadur Shrestha"
    assert "Penicillin" in ram["allergies"]


def test_chatbot_context_patient_ram(client):
    response = client.get("/api/v1/chatbot/context/patient_ram")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_name"] == "Ram Bahadur Shrestha"
    assert "ehr_text" in data
    assert "PATIENT IDENTIFIERS" in data["ehr_text"]
    assert "Penicillin" in data["ehr_text"]


def test_chatbot_general_message(client):
    response = client.post(
        "/api/v1/chatbot/message",
        data={"message": "What is Sanchai?", "patient_id": "patient_ram"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert data["patient_name"] == "Ram Bahadur Shrestha"


def test_chatbot_allergy_contraindication_alert(client):
    # Ram has Penicillin allergy; test asking to prescribe Amoxicillin
    response = client.post(
        "/api/v1/chatbot/message",
        data={
            "message": "Can the doctor give me Amoxicillin for my throat infection?",
            "patient_id": "patient_ram",
        },
    )
    assert response.status_code == 200
    data = response.json()
    alerts = data.get("safety_alerts", [])
    assert len(alerts) >= 1
    assert any("Penicillin" in a and "Amoxicillin" in a for a in alerts)


def test_chatbot_pre_visit_summary(client):
    response = client.post(
        "/api/v1/chatbot/message",
        data={
            "message": "Please generate a pre-visit doctor summary for my hospital appointment tomorrow.",
            "patient_id": "patient_ram",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 50


def test_chatbot_with_file_attachment(client):
    sample_text = "Rx Tab Cetamol 500mg - 1 TDS, खोकी छ, ज्वरो छैन"
    response = client.post(
        "/api/v1/chatbot/message",
        data={
            "message": "Please interpret this uploaded prescription slip.",
            "patient_id": "patient_ram",
        },
        files={"file": ("slip.txt", sample_text.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    attachment = data.get("attachment")
    assert attachment is not None
    assert attachment["filename"] == "slip.txt"
    assert "concepts" in attachment
    assert len(attachment["concepts"]) >= 1
