"""
FastAPI application demonstrating Avro, Protobuf, and JSON Schema endpoints.

This implementation is based on the comprehensive comparison document:
avro-protobuf-jsonschema-context.md
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Optional, cast

from fastapi import FastAPI, HTTPException, Request, Response
from fastavro import parse_schema, schemaless_reader, schemaless_writer
from pydantic import BaseModel, Field

from app.config import get_settings

# Import will work after running: make proto
try:
    from schemas import user_pb2

    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False
    print("Warning: Protobuf module not generated. Run 'make proto' or './generate_proto.sh'")

settings = get_settings()

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": settings.author_name,
        "email": settings.author_email,
        "url": settings.author_github,
    },
)


# ============================================================================
# JSON Endpoint (Pydantic / JSON Schema via OpenAPI)
# ============================================================================


class UserJSON(BaseModel):
    """User model for JSON endpoint using Pydantic validation."""

    id: int = Field(..., ge=1, description="User ID (must be >= 1)")
    name: str = Field(..., min_length=1, description="User name")
    email: Optional[str] = Field(None, description="User email (optional)")
    is_active: bool = Field(True, description="Whether user is active")

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True}]
        }
    }


@app.post("/json/user", response_model=UserJSON, tags=["JSON"])
def json_user(user: UserJSON) -> UserJSON:
    """
    JSON endpoint using Pydantic models.

    FastAPI automatically generates JSON Schema via OpenAPI for this endpoint.

    Content-Type: application/json
    """
    return user


# ============================================================================
# Protobuf Endpoint (application/x-protobuf)
# ============================================================================


@app.post("/protobuf/user", tags=["Protobuf"])
async def protobuf_user(request: Request) -> Response:
    """
    Protobuf endpoint accepting raw binary protobuf messages.

    This endpoint accepts and returns Protocol Buffers binary format.

    Content-Type: application/x-protobuf or application/octet-stream

    Example:
        import user_pb2
        u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)
        data = u.SerializeToString()
        # POST data with Content-Type: application/x-protobuf
    """
    if not PROTOBUF_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Protobuf support not available. Run 'make proto' to generate protobuf code."
        )

    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/x-protobuf", "application/octet-stream"):
        raise HTTPException(
            status_code=415, detail="Use Content-Type: application/x-protobuf or application/octet-stream"
        )

    body = await request.body()
    msg = user_pb2.User()

    try:
        msg.ParseFromString(body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid protobuf payload: {e}")

    if msg.id < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    return Response(content=msg.SerializeToString(), media_type="application/x-protobuf")


# ============================================================================
# Avro Endpoint (application/avro)
# ============================================================================

AVRO_USER_SCHEMA = parse_schema(
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


@app.post("/avro/user", tags=["Avro"])
async def avro_user(request: Request) -> Response:
    """
    Avro endpoint accepting schemaless Avro binary messages.

    This endpoint accepts and returns Avro binary format using schemaless encoding.
    The schema is agreed upon between client and server.

    Content-Type: application/avro or application/octet-stream

    Example:
        from io import BytesIO
        from fastavro import parse_schema
        from fastavro.schemaless_writer import schemaless_writer

        schema = parse_schema({...})  # Same schema as server
        buf = BytesIO()
        schemaless_writer(buf, schema, {"id": 1, "name": "Wallace", ...})
        payload = buf.getvalue()
        # POST payload with Content-Type: application/avro
    """
    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/avro", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Use Content-Type: application/avro or application/octet-stream")

    body = await request.body()
    try:
        record = cast(dict[str, Any], schemaless_reader(BytesIO(body), AVRO_USER_SCHEMA))  # type: ignore[call-arg]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid avro payload: {e}")

    if record.get("id", 0) < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    out = BytesIO()
    schemaless_writer(out, AVRO_USER_SCHEMA, record)
    return Response(content=out.getvalue(), media_type="application/avro")


# ============================================================================
# Health Check & Info Endpoints
# ============================================================================


@app.get("/", tags=["Info"])
def root() -> dict:
    """Root endpoint with API information."""
    return {
        "title": settings.app_title,
        "version": settings.app_version,
        "description": settings.app_description,
        "author": {
            "name": settings.author_name,
            "title": settings.author_title,
            "email": settings.author_email,
            "github": settings.author_github,
            "linkedin": settings.author_linkedin,
            "speakerdeck": settings.author_speakerdeck,
        },
        "endpoints": {
            "json": "/json/user",
            "protobuf": "/protobuf/user",
            "avro": "/avro/user",
        },
        "docs": "/docs",
        "reference": "See avro-protobuf-jsonschema-context.md for detailed comparison",
    }


@app.get("/health", tags=["Info"])
def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "protobuf_available": PROTOBUF_AVAILABLE,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
