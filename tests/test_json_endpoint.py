"""Tests for JSON endpoint."""

from fastapi.testclient import TestClient


def test_json_endpoint_valid_user(client: TestClient) -> None:
    """Test JSON endpoint with valid user data."""
    payload = {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True}

    response = client.post("/json/user", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Wallace"
    assert data["email"] == "wallace@example.com"
    assert data["is_active"] is True


def test_json_endpoint_minimal_user(client: TestClient) -> None:
    """Test JSON endpoint with minimal required fields."""
    payload = {"id": 1, "name": "Test User", "is_active": False}

    response = client.post("/json/user", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test User"
    assert data["email"] is None
    assert data["is_active"] is False


def test_json_endpoint_invalid_id(client: TestClient) -> None:
    """Test JSON endpoint with invalid ID (< 1)."""
    payload = {"id": 0, "name": "Invalid User", "is_active": True}

    response = client.post("/json/user", json=payload)

    assert response.status_code == 422
    assert "greater than or equal to 1" in response.text.lower()


def test_json_endpoint_missing_name(client: TestClient) -> None:
    """Test JSON endpoint with missing required name field."""
    payload = {"id": 1, "is_active": True}

    response = client.post("/json/user", json=payload)

    assert response.status_code == 422


def test_json_endpoint_empty_name(client: TestClient) -> None:
    """Test JSON endpoint with empty name."""
    payload = {"id": 1, "name": "", "is_active": True}

    response = client.post("/json/user", json=payload)

    assert response.status_code == 422
