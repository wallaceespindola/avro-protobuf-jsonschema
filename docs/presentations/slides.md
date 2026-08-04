---
marp: true
theme: gaia
paginate: true
backgroundColor: '#ffffff'
color: '#1a2744'
style: |
  section {
    font-family: 'Helvetica Neue', Arial, sans-serif;
  }
  section.lead {
    background: #0d1b3e;
    color: #ffffff;
  }
  section.lead h1 { color: #4ECDC4; }
  h1, h2 { color: #0d1b3e; }
  section.lead h2 { color: #ffffff; }
  code { font-family: 'Menlo', 'Consolas', monospace; }
  section pre { font-size: 0.7em; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Avro vs Protobuf vs JSON Schema

## Picking the right serialization format for the job

**Wallace Espindola**
Sr. Software Engineer / Solution Architect

wallace.espindola@gmail.com
linkedin.com/in/wallaceespindola | github.com/wallaceespindola

---

# Why does the format even matter?

- Every API call, every Kafka message, every stored record crosses a wire
- The format decides payload size, speed and how safely schemas change
- Pick wrong and you pay in bandwidth, latency or painful migrations
- There is no single winner — each format owns a different boundary
- Today: three formats, one `User` record, one live FastAPI app

---

# The three contenders

| | Born for | Encoding | Ecosystem |
|---|---|---|---|
| **JSON Schema** | Validating JSON contracts | Text | REST, OpenAPI/Swagger |
| **Protobuf** | Fast service-to-service calls | Binary | gRPC, microservices |
| **Avro** | Long-lived streaming data | Binary | Kafka, Spark, Flink |

Same `User` record, three very different wire formats.

---

# Contender 1: JSON Schema

- A standard to describe and validate JSON documents
- Human-readable, browser-native, OpenAPI's backbone

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id":        {"type": "integer", "minimum": 1},
    "name":      {"type": "string", "minLength": 1},
    "email":     {"type": ["string", "null"], "format": "email"},
    "is_active": {"type": "boolean"}
  },
  "required": ["id", "name", "is_active"]
}
```

---

# Contender 2: Protocol Buffers

- Compact binary format with `.proto` definitions and code generation
- Built for speed and tiny payloads — the gRPC native tongue

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

From this repo: `schemas/user.proto` → `protoc --python_out=. user.proto`

---

# Contender 3: Apache Avro

- Binary format designed around **schema evolution**
- Schema travels with the data (or lives in a registry)

```json
{
  "type": "record",
  "name": "User",
  "namespace": "com.example",
  "fields": [
    {"name": "id", "type": "long"},
    {"name": "name", "type": "string"},
    {"name": "email", "type": ["null", "string"], "default": null},
    {"name": "is_active", "type": "boolean", "default": true}
  ]
}
```

---

# Encoding: text vs binary

**JSON — text**
- You can read it, debug it in any browser tab, `curl` it by hand
- Field names repeat in every single payload — verbose on the wire

**Protobuf & Avro — binary**
- No field names on the wire: numbers (Protobuf) or field order (Avro)
- Much smaller payloads, but you need the schema to make sense of bytes
- Debugging means tooling, not eyeballs

---

# Schema evolution: Avro

- The gold standard: **reader schema vs writer schema** resolution
- Reader with a new schema can decode data written with an old one
- Add fields with defaults, remove fields with defaults — both directions work
- That's why Kafka + Schema Registry standardized on it
- Old events stay readable for years — key for long-lived pipelines

---

# Schema evolution: Protobuf

- Fields are identified by **numbers**, not names — rename freely
- Add new fields with new numbers: old readers just skip them
- Never reuse or renumber a field — reserve retired numbers instead
- proto3 gotcha: scalars have defaults; use `optional` for true field presence
- Very good evolution, slightly more discipline required than Avro

---

# Schema evolution: JSON Schema

- No built-in resolution — evolution is a **convention**, not a mechanism
- Version your API (`/v1`, `/v2`) or version the schema document itself
- Loosening rules is safe-ish; tightening breaks existing clients
- `additionalProperties: false` makes every new field a breaking change
- Works fine for REST — just plan versioning up front

---

# Performance: the qualitative hierarchy

**1. Protobuf** — smallest payloads, fastest encode/decode
**2. Avro** — compact binary, close behind, evolution-focused
**3. JSON** — largest and slowest, but nothing beats its reach

- Field names and quotes cost real bytes at scale
- Binary formats shift cost from bandwidth to tooling
- Measure with your own payloads before you commit

---

# Live demo: one app, three formats

The repo runs a FastAPI app serving all three side by side:

```bash
git clone https://github.com/wallaceespindola/avro-protobuf-jsonschema
make proto   # generate user_pb2.py from user.proto
make run     # uvicorn app.main:app --reload
```

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Same `User` record flows through every endpoint

---

# Demo: the three endpoints

| Endpoint | Content-Type | Under the hood |
|---|---|---|
| `POST /json/user` | `application/json` | Pydantic → JSON Schema via OpenAPI |
| `POST /protobuf/user` | `application/x-protobuf` | `user_pb2.ParseFromString()` |
| `POST /avro/user` | `application/avro` | fastavro `schemaless_reader` |

- Binary endpoints accept raw bytes, validate, echo the record back
- Test clients included: `clients/test_protobuf_endpoint.py`, `clients/test_avro_endpoint.py`

---

# Demo: try it with curl

```bash
curl -X POST "http://localhost:8000/json/user" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Wallace",
    "email": "wallace@example.com",
    "is_active": true
  }'
```

- JSON is the only one you can hand-write in a terminal
- For Protobuf and Avro, the Python clients build the binary payloads

---

# Decision framework

| Boundary | Pick | Why |
|---|---|---|
| Public / browser API | **JSON Schema** | Readable, OpenAPI docs, zero client tooling |
| Internal microservices | **Protobuf** | Small, fast, gRPC-native |
| Data pipeline / streaming | **Avro** | Evolution + Kafka Schema Registry |

Ask: *who reads this data, and for how long?*

---

# Real systems use all three

```
Frontend / Public APIs  (JSON + JSON Schema via OpenAPI)
            ↓
      API Gateway / BFF
            ↓
   Internal Services  (Protobuf + gRPC)
            ↓
Event Streaming / Data Platform  (Avro + Kafka + Registry)
```

This isn't overengineering — it's **boundary-driven format selection**.

---

# Key takeaways

- Most used: JSON — the lingua franca of the web
- Fastest and smallest: Protobuf
- Best schema evolution for long-lived data: Avro
- Choose per boundary, not per company
- Clone the repo and run all three in five minutes

---

<!-- _class: lead -->

# Resources

**Repo (app + docs + clients):**
github.com/wallaceespindola/avro-protobuf-jsonschema

**Reference doc:** `docs/avro-protobuf-jsonschema-context.md`

**Wallace Espindola**
wallace.espindola@gmail.com
linkedin.com/in/wallaceespindola | github.com/wallaceespindola

*Thanks! Questions?*
