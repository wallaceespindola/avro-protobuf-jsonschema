"""Tests for Avro endpoint."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from fastavro import parse_schema, schemaless_reader, schemaless_writer


@pytest.fixture
def avro_schema():
    """Avro schema fixture."""
    return parse_schema(
        {
            "type": "record",
            "name": "User",
            "namespace": "com.example",
            "fields": [
                {"name": "id", "type": "long"},
                {"name": "name", "type": "string"},
                {"name": "email", "type": ["null", "string"], "default": None},
                {"name": "is_active", "type": "boolean", "default": True},
            ],
        }
    )


def serialize_avro(schema, record: dict) -> bytes:
    """Helper to serialize record to Avro."""
    buf = BytesIO()
    schemaless_writer(buf, schema, record)
    return buf.getvalue()


def deserialize_avro(schema, data: bytes) -> dict:
    """Helper to deserialize Avro to record."""
    return schemaless_reader(BytesIO(data), schema)


def test_avro_endpoint_valid_user(client: TestClient, avro_schema) -> None:
    """Test Avro endpoint with valid user data."""
    record = {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True}
    payload = serialize_avro(avro_schema, record)

    response = client.post("/avro/user", content=payload, headers={"Content-Type": "application/avro"})

    assert response.status_code == 200
    decoded = deserialize_avro(avro_schema, response.content)
    assert decoded["id"] == 1
    assert decoded["name"] == "Wallace"
    assert decoded["email"] == "wallace@example.com"
    assert decoded["is_active"] is True


def test_avro_endpoint_minimal_user(client: TestClient, avro_schema) -> None:
    """Test Avro endpoint with minimal fields (using defaults)."""
    record = {"id": 2, "name": "Test User", "email": None, "is_active": False}
    payload = serialize_avro(avro_schema, record)

    response = client.post("/avro/user", content=payload, headers={"Content-Type": "application/avro"})

    assert response.status_code == 200
    decoded = deserialize_avro(avro_schema, response.content)
    assert decoded["id"] == 2
    assert decoded["name"] == "Test User"
    assert decoded["email"] is None
    assert decoded["is_active"] is False


def test_avro_endpoint_invalid_id(client: TestClient, avro_schema) -> None:
    """Test Avro endpoint with invalid ID (< 1)."""
    record = {"id": 0, "name": "Invalid", "email": None, "is_active": True}
    payload = serialize_avro(avro_schema, record)

    response = client.post("/avro/user", content=payload, headers={"Content-Type": "application/avro"})

    assert response.status_code == 422
    assert "id must be >= 1" in response.text


def test_avro_endpoint_wrong_content_type(client: TestClient) -> None:
    """Test Avro endpoint with wrong content type."""
    response = client.post("/avro/user", content=b"dummy", headers={"Content-Type": "application/json"})

    assert response.status_code == 415


def test_avro_endpoint_invalid_payload(client: TestClient) -> None:
    """Test Avro endpoint with invalid Avro payload."""
    response = client.post("/avro/user", content=b"invalid avro data", headers={"Content-Type": "application/avro"})

    assert response.status_code == 400
    assert "invalid avro payload" in response.text.lower()
