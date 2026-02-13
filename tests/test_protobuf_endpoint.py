"""Tests for Protobuf endpoint."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path for protobuf import
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from schemas import user_pb2

    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False


pytestmark = pytest.mark.skipif(not PROTOBUF_AVAILABLE, reason="Protobuf module not generated. Run 'make proto' first.")


def test_protobuf_endpoint_valid_user(client: TestClient) -> None:
    """Test Protobuf endpoint with valid user data."""
    if not PROTOBUF_AVAILABLE:
        pytest.skip("Protobuf not available")

    u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)
    payload = u.SerializeToString()

    response = client.post("/protobuf/user", content=payload, headers={"Content-Type": "application/x-protobuf"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-protobuf"

    # Deserialize response
    u2 = user_pb2.User()
    u2.ParseFromString(response.content)
    assert u2.id == 1
    assert u2.name == "Wallace"
    assert u2.email == "wallace@example.com"
    assert u2.is_active is True


def test_protobuf_endpoint_minimal_user(client: TestClient) -> None:
    """Test Protobuf endpoint with minimal fields."""
    if not PROTOBUF_AVAILABLE:
        pytest.skip("Protobuf not available")

    u = user_pb2.User(id=2, name="Test User", email="", is_active=False)
    payload = u.SerializeToString()

    response = client.post("/protobuf/user", content=payload, headers={"Content-Type": "application/x-protobuf"})

    assert response.status_code == 200

    u2 = user_pb2.User()
    u2.ParseFromString(response.content)
    assert u2.id == 2
    assert u2.name == "Test User"
    assert u2.email == ""
    assert u2.is_active is False


def test_protobuf_endpoint_invalid_id(client: TestClient) -> None:
    """Test Protobuf endpoint with invalid ID (< 1)."""
    if not PROTOBUF_AVAILABLE:
        pytest.skip("Protobuf not available")

    u = user_pb2.User(id=0, name="Invalid", email="test@example.com", is_active=True)
    payload = u.SerializeToString()

    response = client.post("/protobuf/user", content=payload, headers={"Content-Type": "application/x-protobuf"})

    assert response.status_code == 422
    assert "id must be >= 1" in response.text


def test_protobuf_endpoint_wrong_content_type(client: TestClient) -> None:
    """Test Protobuf endpoint with wrong content type."""
    response = client.post("/protobuf/user", content=b"dummy", headers={"Content-Type": "application/json"})

    assert response.status_code == 415


def test_protobuf_endpoint_invalid_payload(client: TestClient) -> None:
    """Test Protobuf endpoint with invalid Protobuf payload."""
    response = client.post(
        "/protobuf/user", content=b"invalid protobuf data", headers={"Content-Type": "application/x-protobuf"}
    )

    # Should return 400 or 503 depending on protobuf availability
    assert response.status_code in [400, 503]


def test_protobuf_endpoint_with_octet_stream(client: TestClient) -> None:
    """Test Protobuf endpoint accepts application/octet-stream."""
    if not PROTOBUF_AVAILABLE:
        pytest.skip("Protobuf not available")

    u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)
    payload = u.SerializeToString()

    response = client.post("/protobuf/user", content=payload, headers={"Content-Type": "application/octet-stream"})

    assert response.status_code == 200

    u2 = user_pb2.User()
    u2.ParseFromString(response.content)
    assert u2.id == 1
