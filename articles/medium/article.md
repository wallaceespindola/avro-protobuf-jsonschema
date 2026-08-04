# The Serialization Showdown: Avro, Protobuf and JSON Schema in Real Code

### Three ways to define a data contract, one working FastAPI app to test them all — here's what I learned wiring up each one

![Banner](banner.png)

*By [Wallace Espindola](https://www.linkedin.com/in/wallaceespindola/) — [wallace.espindola@gmail.com](mailto:wallace.espindola@gmail.com) — [GitHub](https://github.com/wallaceespindola/)*

---

A few weeks ago I got asked a question that sounds simple until you actually have to answer it: "Should this new service send JSON or Protobuf?"

The honest answer was "it depends," which is the kind of answer nobody wants in a design review. So instead of hand-waving through it again, I built something concrete: a small FastAPI app with three endpoints (one for JSON, one for Protobuf, one for Avro), all serializing the exact same `User` object. Same fields, same validation rules, three completely different wire formats.

That project became [avro-protobuf-jsonschema](https://github.com/wallaceespindola/avro-protobuf-jsonschema), and this article walks through what I found. Not benchmarks, not vendor slides. Just the actual code, the actual trade-offs and the decision framework I ended up using.

If you've ever sat in a meeting arguing about serialization formats without anyone pulling up real code, this is for you.

## Why the format you pick actually matters

Here's the thing people miss: picking a serialization format isn't a technical detail you bolt on later. It's a contract. Every service that reads your data, every consumer downstream, every future version of your schema has to live with that choice.

Get it wrong and you end up with one of two painful outcomes. Either your APIs are slow and bloated because you shipped verbose JSON where you needed speed, or you've locked yourself into a rigid binary format and now a simple "add an optional field" change breaks three other teams.

The three formats in this comparison solve this problem from completely different angles:

- **JSON Schema** validates and describes JSON documents, the same JSON your browser already speaks.
- **Protocol Buffers (Protobuf)** compiles a `.proto` file into generated code and produces a compact binary payload.
- **Apache Avro** also produces binary, but it leans hard into schema evolution: the schema travels with (or alongside) the data instead of living only in generated code.

None of these is "the best." Each one is the best *for a specific boundary in your system*. Let's build all three and see what that actually feels like in practice.

## The experiment: one User, three formats

The setup is simple. I defined the same logical entity everywhere:

```
id: integer (required, >= 1)
name: string (required, non-empty)
email: string (optional)
is_active: boolean
```

Then I implemented it three times (once as a Pydantic model for JSON, once as a `.proto` message for Protobuf and once as an Avro schema) and wired each one into a FastAPI endpoint. The full project structure looks like this:

```
avro-protobuf-jsonschema/
├── app/
│   └── main.py              # FastAPI application with all endpoints
├── schemas/
│   └── user.proto           # Protobuf schema definition
├── examples/
│   ├── avro_example.py      # Standalone Avro serialization
│   ├── protobuf_example.py  # Standalone Protobuf serialization
│   └── jsonschema_example.py # Standalone JSON Schema validation
├── clients/                 # Test clients for each endpoint
└── tests/                   # Pytest suite
```

You can clone it and run all three examples yourself:

```bash
python examples/jsonschema_example.py
python examples/avro_example.py
python examples/protobuf_example.py   # requires: make proto
```

Let's go through each format the way I did, starting with the one you already know.

## JSON Schema: the format you're already speaking

JSON doesn't need an introduction. What's less obvious is that FastAPI is generating a JSON Schema for you automatically, every time you define a Pydantic model. You get validation, documentation and a contract, all from one class:

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Schemas demo: JSON vs Protobuf vs Avro")


class UserJSON(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    email: str | None = None
    is_active: bool = True


@app.post("/json/user", response_model=UserJSON)
def json_user(user: UserJSON) -> UserJSON:
    return user
```

That's it. No compilation step, no generated stubs. FastAPI turns this model into an OpenAPI schema you can see live at `/docs`, and any client — a browser, curl, a mobile app — can send plain JSON and get plain JSON back.

Here's the standalone version of what's happening underneath, using the `jsonschema` library directly (from `examples/jsonschema_example.py`):

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

invalid_user = {"id": 0, "name": "", "is_active": "yes"}

validator = Draft202012Validator(USER_SCHEMA)
errors = sorted(validator.iter_errors(invalid_user), key=lambda e: e.path)
for e in errors:
    path = ".".join([str(p) for p in e.path]) or "<root>"
    print(f"- {path}: {e.message}")
```

Run that against a bad payload and you get exactly what you'd want in an error log: `id: 0 is less than the minimum of 1`, `name: '' is too short`, `is_active: 'yes' is not of type 'boolean'`. Readable, debuggable, no decoder needed.

**What it felt like:** easy. No build step, no generated code to keep in sync, and every payload is human-readable in a network tab or a log file. The cost is size: JSON is text, so field names and punctuation travel with every single message. For a public API or anything a browser touches, that trade is worth it every time.

## Protobuf: fast, but you pay for it in ceremony

Protobuf flips the JSON approach on its head. Instead of describing the shape of your data in the language you're writing in, you describe it in a `.proto` file, then generate code from it:

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

You compile that with `protoc`:

```bash
protoc --python_out=. schemas/user.proto
```

And you get a generated `user_pb2.py` you import and use like any other class:

```python
from schemas import user_pb2

u = user_pb2.User(id=1, name="Wallace", email="wallace@example.com", is_active=True)
data = u.SerializeToString()

u2 = user_pb2.User()
u2.ParseFromString(data)
```

The FastAPI endpoint has to work harder here, because Protobuf payloads arrive as raw bytes with no field names attached. You need the schema to make sense of them at all:

```python
from fastapi import Request, Response, HTTPException
from schemas import user_pb2

@app.post("/protobuf/user")
async def protobuf_user(request: Request) -> Response:
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

Notice that validation — `if msg.id < 1` — has to happen manually, because unlike Pydantic, Protobuf doesn't know anything about your business rules. It only knows the wire format.

**What it felt like:** fast to run, slower to set up. Every schema change means re-running `protoc` and shipping generated code alongside your app. I hit this directly in the repo itself: the endpoint checks `PROTOBUF_AVAILABLE` and returns a 503 if you forgot to run `make proto`. That's not a bug, it's the format being honest about its dependency on code generation. The payoff is a genuinely compact binary payload with no field names traveling over the wire, which is worth it when you control both ends of the connection, like in an internal gRPC service.

One gotcha worth flagging: in proto3, an empty string and a missing string look identical on the wire. If you need to know the difference between "the email field was never set" and "the email field was set to empty," you need `optional` or a wrapper type. It's a small detail, but it's bitten more than one team I've worked with.

## Avro: binary, but the schema travels with the conversation

Avro sits in an interesting middle ground. It's binary like Protobuf, but instead of generating code from a `.proto` file, you work with a schema as a plain Python dict, and both sides need to agree on it at read and write time.

Here's the schema and a full round-trip, straight from `examples/avro_example.py`:

```python
from io import BytesIO
from fastavro import parse_schema, reader, writer

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

buf2 = BytesIO(avro_bytes)
decoded = list(reader(buf2))
```

Notice the `["null", "string"]` union type for `email` and the `"default": None` — that's Avro's schema evolution story in miniature. Fields carry defaults, and unions declare explicitly what "optional" means at the schema level, not as an afterthought.

The FastAPI version uses "schemaless" Avro, which is what you'd do over plain HTTP where you don't want the overhead of embedding the schema in every message:

```python
from io import BytesIO
from fastapi import Request, Response, HTTPException
from fastavro import parse_schema, schemaless_reader, schemaless_writer

AVRO_USER_SCHEMA = parse_schema({
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

@app.post("/avro/user")
async def avro_user(request: Request) -> Response:
    ct = request.headers.get("content-type", "").split(";")[0].strip()
    if ct not in ("application/avro", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Use Content-Type: application/avro")

    body = await request.body()
    try:
        record = schemaless_reader(BytesIO(body), AVRO_USER_SCHEMA, None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid avro payload: {e}") from e

    if record.get("id", 0) < 1:
        raise HTTPException(status_code=422, detail="id must be >= 1")

    out = BytesIO()
    schemaless_writer(out, AVRO_USER_SCHEMA, record)
    return Response(content=out.getvalue(), media_type="application/avro")
```

**What it felt like:** the schema is a plain dict, not a generated class, so there's no compile step in the loop: you can iterate on it as fast as you can edit Python. That's genuinely nice for prototyping. But that flexibility comes with responsibility: since the payload has no field names or type tags of its own, the reader absolutely must have a compatible schema, or decoding fails outright. That's exactly why Avro is almost never used standalone in production. It's usually paired with a schema registry (Kafka's, for example) so producers and consumers can look up the exact schema version a message was written with.

## Side-by-side: what actually changes between the three

Here's the comparison table straight from the project's own reference doc: no invented numbers, just the qualitative shape of the trade-offs.

| Feature | JSON | Protobuf | Avro |
|---|---|---|---|
| Encoding | Text | Binary | Binary |
| Human-readable payload | Yes | No | No |
| Payload size | Larger | Smallest | Small |
| Schema evolution | Moderate | Very good | Excellent |
| Browser friendly | Yes | No | No |
| Typical home | Public REST APIs | gRPC, internal services | Kafka, data pipelines |

Notice what doesn't change: none of these formats is objectively "faster" or "better" in a vacuum. The table is really describing three different bets on what matters most: readability, raw compactness or long-term schema flexibility.

## What each format is actually for

Once you've written all three, the use cases stop being abstract advice and start being obvious from the code itself.

**JSON Schema** wins when a human — or a browser, or a debugging engineer at 2am — needs to read the payload without a decoder ring. It's the natural choice for public APIs and anything documented with OpenAPI/Swagger, which FastAPI gives you for free.

**Protobuf** wins when you control both ends of the wire and performance matters more than readability. That's internal microservices, gRPC calls, anything where shaving bytes and CPU cycles off millions of calls per day adds up. The cost is the build step and the discipline of managing generated code.

**Avro** wins when your data outlives your code. If you're writing events to Kafka that will be read by services that don't exist yet, written by teams who haven't joined the company yet, schema evolution isn't a nice-to-have — it's the whole point. Pairing it with a schema registry is what makes that promise real.

## The pattern I ended up using

The project's README lays out the pattern that most mature systems converge on, and after building this, I believe it:

```
Frontend / Public APIs (JSON + JSON Schema via OpenAPI)
                ↓
        API Gateway / BFF
                ↓
   Internal Services (Protobuf + gRPC)
                ↓
Event Streaming / Data Platform (Avro + Kafka + Schema Registry)
```

This isn't over-engineering. It's picking the right contract for the right boundary. Your public API stays JSON because your frontend team and your API consumers need it readable. Your internal services talk Protobuf because that traffic never leaves your cluster and every millisecond counts. Your event stream uses Avro because five years from now, someone will need to read data written today, by a schema that's changed six times since.

## Try it yourself

Everything in this article runs. Clone the repo, spin up the server, and hit all three endpoints yourself:

```bash
git clone https://github.com/wallaceespindola/avro-protobuf-jsonschema
cd avro-protobuf-jsonschema
make install
make proto     # generates the Protobuf Python stubs
make run       # starts the FastAPI server on :8000
```

Then test each format with the provided clients:

```bash
./clients/test_json_endpoint.sh
python clients/test_protobuf_endpoint.py
python clients/test_avro_endpoint.py
```

Swagger UI is at `http://localhost:8000/docs` if you want to poke at the JSON endpoint interactively. The full reference document with every code example in this article — plus the standalone scripts and the test suite — lives in the repo, not just in this post.

## Wrapping up

Three formats, one entity, and a lot less confusion than I started with. Here's the short version:

- JSON Schema is the format you already know: pick it for anything public or browser-facing.
- Protobuf trades a build step for a genuinely compact, fast binary payload: pick it for internal service-to-service calls.
- Avro trades standalone simplicity for serious schema evolution: pick it for anything flowing through a data pipeline or event stream.
- None of them is wrong. The mistake is picking one format for every boundary in your system instead of matching the format to the job.
- The best way to understand the trade-offs isn't reading a comparison table. It's writing the same object three times and feeling the difference yourself.

If you want to go deeper, the full reference doc in the repo covers client examples for testing each endpoint and more notes on the pitfalls I ran into along the way.

What's your default pick when a new service needs a serialization format? Let me know your thoughts in the comments.

---

Need more tech insights?
Check out my GitHub, LinkedIn, and Speaker Deck.
Happy coding!

[GitHub](https://github.com/wallaceespindola/) · [LinkedIn](https://www.linkedin.com/in/wallaceespindola/)
