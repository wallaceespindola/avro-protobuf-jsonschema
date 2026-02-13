# Avro vs Protobuf vs JSON Schema
*A practical, developer-focused comparison — plus code examples and FastAPI endpoints (JSON / Protobuf / Avro).*

---

## Table of Contents

1. Context: What we compared and why  
2. Quick definitions  
3. High-level comparison table  
4. Which one is “best” and which is most used?  
5. Code examples (standalone)  
   - Avro: schema + serialize/deserialize (Python)  
   - Protobuf: `.proto` + serialize/deserialize (Python)  
   - JSON Schema: schema + validation (Python)  
6. FastAPI endpoints for all three  
   - JSON (Pydantic / JSON Schema via OpenAPI)  
   - Protobuf (`application/x-protobuf`)  
   - Avro (`application/avro`)  
7. Client examples to test each endpoint  
8. Real-world architecture pattern (common in production)  
9. Practical notes & pitfalls  

---

## 1) Context: what we compared and why

We discussed **three popular ways to define and enforce data contracts**:

- **Apache Avro** (binary serialization + schema evolution, common in data platforms)
- **Protocol Buffers (Protobuf)** (binary serialization optimized for speed and bandwidth, common in microservices / gRPC)
- **JSON Schema** (validation + contract definition for JSON, common in REST/OpenAPI)

The goal was to compare them in terms of **where they fit**, **trade-offs**, **usage**, and then provide **code examples** and **FastAPI endpoints** for all three.

---

## 2) Quick definitions

### Avro
A binary serialization format with strong support for **schema evolution**; widely used in **Kafka + data pipeline** ecosystems.

### Protobuf
A compact binary format with `.proto` definitions and **code generation**; widely used for **internal APIs** and **gRPC**.

### JSON Schema
A standard for describing and validating **JSON documents**; commonly used for **REST APIs** and **OpenAPI** contracts.

---

## 3) High-level comparison table

| Feature | **Avro** | **Protobuf** | **JSON Schema** |
|---|---|---|---|
| Primary use | Data pipelines & streaming | Service-to-service APIs | JSON validation & REST APIs |
| Encoding | Binary | Binary (very compact) | Text (JSON) |
| Human-readable payload | ❌ | ❌ | ✅ |
| Schema location | Often stored with data / registry | Separate `.proto` files | Separate JSON schema (often via OpenAPI) |
| Schema evolution | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very good | ⭐⭐⭐ Moderate |
| Performance | High | **Very high** | Low–medium |
| Browser friendliness | ❌ | ❌ | ✅ |
| Typical ecosystem | Kafka, Spark, Flink | gRPC, microservices | OpenAPI/Swagger, REST |

---

## 4) Which one is “best” and which is most used?

### Most used overall
**JSON Schema (via JSON / REST / OpenAPI)** tends to be the most broadly used because web APIs and browser-facing systems commonly exchange JSON.

### “Best” depends on the boundary
- **Best performance & smallest payloads:** **Protobuf**
- **Best schema evolution for long-lived streaming data:** **Avro**
- **Best for public/browser-friendly APIs:** **JSON Schema**

A common real-world approach is to use **more than one** in different layers of the system.

---

## 5) Code examples (standalone)

### 5.1 Avro (Python) — schema + serialize/deserialize

**Install**
```bash
pip install fastavro
```

**Example**
```python
from io import BytesIO
from fastavro import writer, reader, parse_schema

USER_SCHEMA = {
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

parsed_schema = parse_schema(USER_SCHEMA)

records = [
    {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True},
    {"id": 2, "name": "Nia", "email": None, "is_active": False},
]

buf = BytesIO()
writer(buf, parsed_schema, records)
avro_bytes = buf.getvalue()
print("Avro bytes length:", len(avro_bytes))

buf2 = BytesIO(avro_bytes)
decoded = list(reader(buf2))
print(decoded)
```

> Note: For streaming systems (Kafka), Avro is commonly paired with a **schema registry**.

---

### 5.2 Protobuf — `.proto` + serialize/deserialize (Python)

**Install**
```bash
pip install protobuf
```

**`user.proto`**
```proto
syntax = "proto3";

package com.example;

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;       // proto3: empty string means "default"
  bool is_active = 4;
}
```

**Generate Python**
```bash
protoc --python_out=. user.proto
```

**Use it**
```python
import user_pb2

u = user_pb2.User(
    id=1,
    name="Wallace",
    email="wallace@example.com",
    is_active=True
)

data = u.SerializeToString()
print("Protobuf bytes length:", len(data))

u2 = user_pb2.User()
u2.ParseFromString(data)
print("Decoded:", u2)
```

> Note on presence: proto3 uses defaults; if you need true “field presence” for scalars, use `optional` or wrapper types.

---

### 5.3 JSON Schema — schema + validate JSON

**Install**
```bash
pip install jsonschema
```

**Example**
```python
from jsonschema import Draft202012Validator

USER_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": ["string", "null"], "format": "email"},
        "is_active": {"type": "boolean"},
    },
    "required": ["id", "name", "is_active"],
}

valid_user = {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True}
invalid_user = {"id": 0, "name": "", "is_active": "yes"}

validator = Draft202012Validator(USER_SCHEMA)

errors = sorted(validator.iter_errors(invalid_user), key=lambda e: e.path)
for e in errors:
    path = ".".join([str(p) for p in e.path]) or "<root>"
    print(f"- {path}: {e.message}")
```

---

## 6) FastAPI endpoints for all three

### 6.0 Setup

**Install**
```bash
pip install fastapi uvicorn pydantic fastavro protobuf jsonschema
```

**Run**
```bash
uvicorn main:app --reload
```

---

### 6.1 JSON endpoint (Pydantic / JSON Schema via OpenAPI)

FastAPI already generates JSON Schema (via OpenAPI) for your Pydantic models.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Schemas demo: JSON vs Protobuf vs Avro")

class UserJSON(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    is_active: bool = True

@app.post("/json/user", response_model=UserJSON)
def json_user(user: UserJSON) -> UserJSON:
    return user
```

---

### 6.2 Protobuf endpoint (`application/x-protobuf`)

This endpoint accepts **raw bytes** and parses them using the generated `user_pb2.py`.

```python
from fastapi import Request, Response, HTTPException
import user_pb2

@app.post("/protobuf/user")
async def protobuf_user(request: Request) -> Response:
    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/x-protobuf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Use Content-Type: application/x-protobuf")

    body = await request.body()
    msg = user_pb2.User()

    try:
        msg.ParseFromString(body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid protobuf payload: {e}")

    if msg.id < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    return Response(content=msg.SerializeToString(), media_type="application/x-protobuf")
```

---

### 6.3 Avro endpoint (`application/avro`)

This endpoint accepts **raw bytes** encoded using Avro (schemaless), using a schema the server and clients agree on.

```python
from io import BytesIO
from fastapi import Request, Response, HTTPException
from fastavro import parse_schema
from fastavro.schemaless_reader import schemaless_reader
from fastavro.schemaless_writer import schemaless_writer

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

@app.post("/avro/user")
async def avro_user(request: Request) -> Response:
    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/avro", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Use Content-Type: application/avro")

    body = await request.body()
    bio = BytesIO(body)

    try:
        record = schemaless_reader(bio, AVRO_USER_SCHEMA)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid avro payload: {e}")

    if record.get("id", 0) < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    out = BytesIO()
    schemaless_writer(out, AVRO_USER_SCHEMA, record)
    return Response(content=out.getvalue(), media_type="application/avro")
```

---

### 6.4 Full `main.py` in one file (copy/paste)

If you want everything in one place, here is a complete `main.py` that includes all endpoints above:

```python
from __future__ import annotations

from io import BytesIO
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel, Field

from fastavro import parse_schema
from fastavro.schemaless_reader import schemaless_reader
from fastavro.schemaless_writer import schemaless_writer

import user_pb2  # generated from user.proto

app = FastAPI(title="Schemas demo: JSON vs Protobuf vs Avro")

class UserJSON(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    is_active: bool = True

@app.post("/json/user", response_model=UserJSON)
def json_user(user: UserJSON) -> UserJSON:
    return user

@app.post("/protobuf/user")
async def protobuf_user(request: Request) -> Response:
    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/x-protobuf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Use Content-Type: application/x-protobuf")

    body = await request.body()
    msg = user_pb2.User()
    try:
        msg.ParseFromString(body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid protobuf payload: {e}")

    if msg.id < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    return Response(content=msg.SerializeToString(), media_type="application/x-protobuf")

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

@app.post("/avro/user")
async def avro_user(request: Request) -> Response:
    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/avro", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Use Content-Type: application/avro")

    body = await request.body()
    try:
        record = schemaless_reader(BytesIO(body), AVRO_USER_SCHEMA)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid avro payload: {e}")

    if record.get("id", 0) < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    out = BytesIO()
    schemaless_writer(out, AVRO_USER_SCHEMA, record)
    return Response(content=out.getvalue(), media_type="application/avro")
```

---

## 7) Client examples to test each endpoint

### 7.1 JSON (curl)
```bash
curl -X POST "http://127.0.0.1:8000/json/user"   -H "Content-Type: application/json"   -d '{"id":1,"name":"Wallace","email":"wallace@example.com","is_active":true}'
```

### 7.2 Protobuf (Python client)
```python
import requests
import user_pb2

u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)
data = u.SerializeToString()

r = requests.post(
    "http://127.0.0.1:8000/protobuf/user",
    data=data,
    headers={"Content-Type": "application/x-protobuf"},
)
r.raise_for_status()

u2 = user_pb2.User()
u2.ParseFromString(r.content)
print(u2)
```

### 7.3 Avro (Python client)
```python
import requests
from io import BytesIO
from fastavro import parse_schema
from fastavro.schemaless_writer import schemaless_writer
from fastavro.schemaless_reader import schemaless_reader

schema = parse_schema({
    "type": "record",
    "name": "User",
    "namespace": "com.example",
    "fields": [
        {"name": "id", "type": "long"},
        {"name": "name", "type": "string"},
        {"name": "email", "type": ["null", "string"], "default": None},
        {"name": "is_active", "type": "boolean", "default": True},
    ],
})

buf = BytesIO()
schemaless_writer(buf, schema, {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True})
payload = buf.getvalue()

r = requests.post(
    "http://127.0.0.1:8000/avro/user",
    data=payload,
    headers={"Content-Type": "application/avro"},
)
r.raise_for_status()

decoded = schemaless_reader(BytesIO(r.content), schema)
print(decoded)
```

---

## 8) Real-world architecture pattern (common in production)

Many mature systems use **all three** where they fit best:

```
Frontend / Public APIs (JSON + JSON Schema via OpenAPI)
                ↓
        API Gateway / BFF
                ↓
   Internal Services (Protobuf + gRPC)
                ↓
Event Streaming / Data Platform (Avro + Kafka + Schema Registry)
```

This is not overengineering — it is **boundary-driven format selection**.

---

## 9) Practical notes & pitfalls

- **JSON Schema / REST**: easiest for humans and browsers; verbose payloads; great tooling with OpenAPI.
- **Protobuf**: best for internal performance; consider field presence semantics in proto3 when defaults matter.
- **Avro**: best for long-lived event data; for HTTP you typically use “schemaless” Avro with an agreed schema; for Kafka you usually add a schema registry.

### Content types
- JSON: `application/json`
- Protobuf: `application/x-protobuf` (often) or `application/octet-stream`
- Avro: `application/avro` (often) or `application/octet-stream`

---

### TL;DR
- **Most used**: JSON / JSON Schema (especially with REST/OpenAPI)
- **Fastest**: Protobuf
- **Best for evolution in pipelines**: Avro
