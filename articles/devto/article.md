---
title: "I Built the Same API Three Times: JSON, Protobuf and Avro Side by Side"
published: false
description: "One FastAPI app, three /user endpoints - JSON, Protobuf and Avro - so you can see how each format actually behaves, not just read about it."
tags: python, fastapi, protobuf, avro
---

![Banner](banner.png)

Every few months someone on my team asks the same question: "should this endpoint use JSON or something binary?" And every time, the answer is "it depends," followed by a slide deck nobody remembers a week later.

So instead of another slide deck, I built a small FastAPI app with the exact same `User` resource exposed three ways - `/json/user`, `/protobuf/user` and `/avro/user`. Same fields, same validation rules, three different wire formats. You send a user in, you get the same user back, serialized the way you asked for it.

The full project is here: [avro-protobuf-jsonschema on GitHub](https://github.com/wallaceespindola/avro-protobuf-jsonschema). Clone it, run `make run`, and you can hit all three endpoints yourself in about five minutes.

This article walks through the real code from that repo - not simplified pseudo-code, the actual `app/main.py`.

## Why bother comparing them at all

JSON is what most of us reach for by default, and honestly, that's fine most of the time. It's readable, every language parses it, and your browser's dev tools show it without any extra tooling.

But "fine by default" isn't the same as "right for every boundary." Once you're passing millions of events into Kafka, or your gRPC services are chatting with each other a thousand times a second, JSON's overhead starts to matter. That's where Protobuf and Avro come in - and they solve slightly different problems.

Here's the short version, straight from the project's [comparison table](https://github.com/wallaceespindola/avro-protobuf-jsonschema/blob/main/docs/avro-protobuf-jsonschema-context.md):

| Feature | JSON | Protobuf | Avro |
|---|---|---|---|
| Encoding | Text | Binary | Binary |
| Human-readable | Yes | No | No |
| Payload size | Large | Very small | Small |
| Schema evolution | Moderate | Very good | Excellent |
| Typical home | Public REST APIs | Internal microservices, gRPC | Kafka, data pipelines |

None of these numbers are benchmarks I ran - they're qualitative, from the reference doc in the repo. If you need hard numbers for your own payloads, measure them yourself; the size difference depends heavily on your actual field types and string lengths.

## The one User, three ways

All three endpoints model the same four fields: `id`, `name`, `email` and `is_active`. Let's look at how each format defines that shape.

### JSON: a Pydantic model

FastAPI already generates JSON Schema for you through OpenAPI, so the JSON side barely needs any extra work. Here's the actual model from `app/main.py`:

```python
class UserJSON(BaseModel):
    """User model for JSON endpoint using Pydantic validation."""

    id: int = Field(..., ge=1, description="User ID (must be >= 1)")
    name: str = Field(..., min_length=1, description="User name")
    email: str | None = Field(None, description="User email (optional)")
    is_active: bool = Field(True, description="Whether user is active")


@app.post("/json/user", response_model=UserJSON, tags=["JSON"])
def json_user(user: UserJSON) -> UserJSON:
    """
    JSON endpoint using Pydantic models.

    FastAPI automatically generates JSON Schema via OpenAPI for this endpoint.

    Content-Type: application/json
    """
    return user
```

Send it a JSON body, Pydantic validates it (`id >= 1`, `name` not empty), and you get the same object back. Nothing fancy, and that's the point.

### Protobuf: a `.proto` contract plus generated code

Protobuf works differently. You define the message shape in a `.proto` file first, then generate Python classes from it. Here's `schemas/user.proto`, in full:

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

Notice those numbers after each field (`= 1`, `= 2`...). Those are field tags, and they're what makes Protobuf's binary format so compact - the wire format encodes the tag number, not the field name. They're also central to how you evolve the schema later: you can add new fields with new tag numbers, but you should never reuse or renumber an existing one, or old and new clients will start reading each other's data wrong.

Run `make proto` (or `protoc --python_out=. schemas/user.proto` directly) and you get `user_pb2.py` with a generated `User` class. The endpoint that uses it:

```python
@app.post("/protobuf/user", tags=["Protobuf"])
async def protobuf_user(request: Request) -> Response:
    """
    Protobuf endpoint accepting raw binary protobuf messages.

    Content-Type: application/x-protobuf or application/octet-stream
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
        raise HTTPException(status_code=400, detail=f"Invalid protobuf payload: {e}") from e

    if msg.id < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    return Response(content=msg.SerializeToString(), media_type="application/x-protobuf")
```

A few things worth calling out here, because they trip people up the first time:

- FastAPI doesn't know how to auto-parse Protobuf bodies, so you read `await request.body()` as raw bytes yourself and parse them with `ParseFromString`.
- Content-type checking is manual too - there's no built-in dependency for that here, so the endpoint checks it and returns a 415 if it's wrong.
- Validation (`id >= 1`) also has to be written by hand, since you're past Pydantic at this point.

### Avro: schema as a Python dict, no code generation

Avro takes yet another approach. Instead of generating classes from a schema file, you define the schema as a plain dict and pass it to `fastavro` at request time. From `app/main.py`:

```python
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

    Content-Type: application/avro or application/octet-stream
    """
    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/avro", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Use Content-Type: application/avro or application/octet-stream")

    body = await request.body()
    try:
        record = cast(dict[str, Any], schemaless_reader(BytesIO(body), AVRO_USER_SCHEMA, None))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid avro payload: {e}") from e

    if record.get("id", 0) < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    out = BytesIO()
    schemaless_writer(out, AVRO_USER_SCHEMA, record)
    return Response(content=out.getvalue(), media_type="application/avro")
```

Two things stand out compared to the Protobuf version. First, no code generation step - the schema lives right in the app, as data. Second, this is "schemaless" Avro, meaning the payload on the wire has no embedded schema at all. Both sides just have to agree on it ahead of time. That's the same deal you'd get with a Kafka schema registry: the registry holds the schema, the messages just carry an ID pointing to it, and you never ship the schema itself over the wire on every message.

The `email` field is defined as `["null", "string"]` - a union type. That's Avro's way of saying "this can be null or a string," and it's also the mechanism Avro uses for backward-compatible schema evolution: add a new field with a default, and old readers/writers keep working without changes.

## Trying all three yourself

Clone the repo, install dependencies, and generate the Protobuf stubs:

```bash
git clone https://github.com/wallaceespindola/avro-protobuf-jsonschema.git
cd avro-protobuf-jsonschema
./setup.sh          # creates venv, installs deps, generates protobuf code
make run            # starts uvicorn on port 8000
```

### Hit the JSON endpoint with curl

This one's straightforward since it's just JSON over HTTP - straight from `clients/test_json_endpoint.sh`:

```bash
curl -X POST "http://127.0.0.1:8000/json/user" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Wallace",
    "email": "wallace@example.com",
    "is_active": true
  }' | jq .
```

### Hit the Protobuf endpoint with Python

Curl can't build a Protobuf payload for you, so the repo ships a small Python client instead - `clients/test_protobuf_endpoint.py`:

```python
from schemas import user_pb2
import requests

u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)
data = u.SerializeToString()

r = requests.post(
    "http://127.0.0.1:8000/protobuf/user",
    data=data,
    headers={"Content-Type": "application/x-protobuf"},
    timeout=5,
)
r.raise_for_status()

u2 = user_pb2.User()
u2.ParseFromString(r.content)
print(u2)
```

Run it with `python clients/test_protobuf_endpoint.py` once the server is up.

### Hit the Avro endpoint with Python

Same story here - `clients/test_avro_endpoint.py`:

```python
from io import BytesIO
import requests
from fastavro import parse_schema, schemaless_reader, schemaless_writer

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

user = {"id": 1, "name": "Wallace", "email": "wallace@example.com", "is_active": True}

buf = BytesIO()
schemaless_writer(buf, schema, user)
payload = buf.getvalue()

r = requests.post(
    "http://127.0.0.1:8000/avro/user",
    data=payload,
    headers={"Content-Type": "application/avro"},
    timeout=5,
)
r.raise_for_status()

decoded = schemaless_reader(BytesIO(r.content), schema)
print(decoded)
```

Run it with `python clients/test_avro_endpoint.py`.

Notice the pattern across both binary clients: the client has to hold the exact same schema (or generated stub) as the server. There's no discovery mechanism here - that's the trade-off you're accepting for the smaller payload and faster parsing.

## Gotchas I ran into building this

**Protobuf needs a build step before the app even starts.** If you forget to run `make proto`, the app still boots, but the endpoint returns a 503 with a message telling you to generate the code first - you can see that check right at the top of `protobuf_user`. It's a small thing, but it's easy to forget when you're switching branches.

**proto3 doesn't really have "unset."** Look at the `.proto` file comment: `string email = 3; // proto3: empty string means "default"`. If a client doesn't set `email`, you get back an empty string, not `None`. If you genuinely need to tell "empty" apart from "never set," you'd reach for `optional` or a wrapper type - this demo keeps it simple and doesn't need that distinction.

**Avro's schemaless mode has no self-describing payload.** Open the Protobuf or Avro bytes in a text editor and you'll see gibberish either way - but with Avro schemaless encoding specifically, there's no schema fingerprint or ID embedded either. If your client and server schemas drift out of sync, you won't get a friendly error - you'll get garbage data or a decode exception. In production Kafka setups this is exactly why teams add a schema registry on top: the registry becomes the single source of truth both sides check against.

**Content-type checking is entirely manual for the binary endpoints.** FastAPI's automatic body parsing is built around JSON. For Protobuf and Avro, both endpoints read `request.headers.get("content-type")` themselves and return a 415 if it doesn't match. Worth remembering if you're building your own binary endpoint from scratch - there's no decorator that does this for you.

## What I'd actually pick, and when

Based on what's in the repo and the [comparison notes](https://github.com/wallaceespindola/avro-protobuf-jsonschema/blob/main/docs/avro-protobuf-jsonschema-context.md):

- **Public or browser-facing API?** Stick with JSON. Your payload is readable, every client library speaks it, and OpenAPI docs come for free with FastAPI and Pydantic.
- **Internal service-to-service calls, especially with gRPC?** Protobuf. The compact binary format and generated stubs pay off once you're making thousands of calls between services.
- **Streaming into Kafka or a data lake?** Avro. Its schema evolution model is built for data that outlives the code that wrote it, which is exactly the situation you're in with long-lived event streams.

A lot of real systems end up using all three at different boundaries - JSON at the edge, Protobuf between internal services, Avro in the event pipeline. That's not overengineering, it's just matching the format to the job at each layer.

## Try it yourself

Clone [the repo](https://github.com/wallaceespindola/avro-protobuf-jsonschema), run `make run`, and hit all three endpoints with the clients above. The test suite (`make test`) is a good second stop if you want to see how each format's edge cases get covered.

What's your approach? Drop it in the comments.

Need more tech insights?
Check out my GitHub, LinkedIn, and Speaker Deck.
Happy coding!

- GitHub: https://github.com/wallaceespindola/
- LinkedIn: https://www.linkedin.com/in/wallaceespindola/
