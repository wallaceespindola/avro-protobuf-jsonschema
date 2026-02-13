"""Tests for health and info endpoints."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns API info."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "endpoints" in data
    assert "json" in data["endpoints"]
    assert "protobuf" in data["endpoints"]
    assert "avro" in data["endpoints"]


def test_health_endpoint(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "protobuf_available" in data
