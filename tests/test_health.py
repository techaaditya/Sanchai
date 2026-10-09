import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "sanchai-api"
    assert "status" in data
    assert "model_backend" in data
    assert "model" in data
    assert isinstance(data["services"], list)
