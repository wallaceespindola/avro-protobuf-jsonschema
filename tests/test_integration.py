"""Integration tests for the complete API."""

from io import BytesIO

from fastapi.testclient import TestClient
from fastavro import parse_schema, schemaless_reader, schemaless_writer


def test_api_documentation_available(client: TestClient) -> None:
    """Test that API documentation is accessible."""
    # OpenAPI JSON
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "/json/user" in data["paths"]
    assert "/protobuf/user" in data["paths"]
    assert "/avro/user" in data["paths"]

    # Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200

    # ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_has_contact_info(client: TestClient) -> None:
    """Test that OpenAPI spec includes contact information."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "info" in data
    assert "contact" in data["info"]
    assert "name" in data["info"]["contact"]
    assert "email" in data["info"]["contact"]


def test_all_endpoints_listed_in_root(client: TestClient) -> None:
    """Test that root endpoint lists all available endpoints."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "endpoints" in data
    assert data["endpoints"]["json"] == "/json/user"
    assert data["endpoints"]["protobuf"] == "/protobuf/user"
    assert data["endpoints"]["avro"] == "/avro/user"


def test_author_info_in_root(client: TestClient) -> None:
    """Test that author information is included in root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "author" in data
    assert "name" in data["author"]
    assert "title" in data["author"]
    assert "email" in data["author"]
    assert "github" in data["author"]
    assert "linkedin" in data["author"]
    assert "speakerdeck" in data["author"]


def test_health_check_shows_protobuf_status(client: TestClient) -> None:
    """Test health check includes Protobuf availability status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "protobuf_available" in data
    assert isinstance(data["protobuf_available"], bool)


def test_json_endpoint_round_trip(client: TestClient) -> None:
    """Test complete round trip for JSON endpoint."""
    payload = {"id": 42, "name": "Integration Test", "email": "integration@test.com", "is_active": True}

    response = client.post("/json/user", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == payload["id"]
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["is_active"] == payload["is_active"]


def test_avro_endpoint_round_trip(client: TestClient) -> None:
    """Test complete round trip for Avro endpoint."""
    schema = parse_schema(
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

    record = {"id": 42, "name": "Integration Test", "email": "integration@test.com", "is_active": True}

    # Serialize
    buf = BytesIO()
    schemaless_writer(buf, schema, record)
    payload = buf.getvalue()

    # Send request
    response = client.post("/avro/user", content=payload, headers={"Content-Type": "application/avro"})
    assert response.status_code == 200

    # Deserialize response
    decoded = schemaless_reader(BytesIO(response.content), schema)
    assert decoded["id"] == record["id"]
    assert decoded["name"] == record["name"]
    assert decoded["email"] == record["email"]
    assert decoded["is_active"] == record["is_active"]


def test_different_formats_same_data(client: TestClient) -> None:
    """Test that all formats can represent the same user data."""
    user_data = {"id": 100, "name": "Format Test", "email": "format@test.com", "is_active": True}

    # Test JSON
    json_response = client.post("/json/user", json=user_data)
    assert json_response.status_code == 200
    json_result = json_response.json()

    # Test Avro
    schema = parse_schema(
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

    buf = BytesIO()
    schemaless_writer(buf, schema, user_data)
    avro_payload = buf.getvalue()

    avro_response = client.post("/avro/user", content=avro_payload, headers={"Content-Type": "application/avro"})
    assert avro_response.status_code == 200
    avro_result = schemaless_reader(BytesIO(avro_response.content), schema)

    # Both should have the same data
    assert json_result["id"] == avro_result["id"]
    assert json_result["name"] == avro_result["name"]
    assert json_result["email"] == avro_result["email"]
    assert json_result["is_active"] == avro_result["is_active"]


def test_cors_not_enabled_by_default(client: TestClient) -> None:
    """Test that CORS is not enabled by default (can be enabled if needed)."""
    response = client.get("/", headers={"Origin": "http://example.com"})
    # CORS headers should not be present unless explicitly configured
    assert "access-control-allow-origin" not in response.headers.keys()
