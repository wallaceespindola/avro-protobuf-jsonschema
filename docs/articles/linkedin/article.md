---
author: Wallace Espindola
email: wallace.espindola@gmail.com
linkedin: https://www.linkedin.com/in/wallaceespindola/
github: https://github.com/wallaceespindola/
---

# Avro vs Protobuf vs JSON Schema: Which One Belongs in Your Architecture?

![Banner](banner.png)

I keep seeing the same argument in architecture reviews: "let's just use JSON everywhere" versus "we need Protobuf for performance" versus "Avro is the only real answer for streaming." Truth is, all three camps are right, just about different parts of the system.

I put together a small, runnable FastAPI project that implements the same `User` resource three times, once with JSON, once with Protobuf, and once with Avro, so you can actually see the differences instead of arguing about them in the abstract. It's open source here: [avro-protobuf-jsonschema on GitHub](https://github.com/wallaceespindola/avro-protobuf-jsonschema).

## The problem with picking "one format to rule them all"

Every serialization format optimizes for something different. JSON optimizes for humans reading it. Protobuf optimizes for bytes on the wire. Avro optimizes for schemas that change over years without breaking old data.

If you force one format across your whole stack, you're accepting a trade-off somewhere you didn't need to. A public REST API doesn't need Protobuf's compactness. A Kafka topic storing years of event data doesn't want plain JSON with no schema evolution story. Picking the right tool per boundary isn't overengineering, it's just matching the format to the job.

## Quick definitions, no fluff

**JSON Schema** describes and validates JSON documents. It's the format most REST APIs and OpenAPI specs already speak.

**Protobuf** (Protocol Buffers) is Google's compact binary format. You define messages in a `.proto` file, generate code from it, and get small, fast payloads. It's the backbone of most gRPC services.

**Avro** is a binary format built around schema evolution. It's the default choice in Kafka and big data pipelines because it handles schema changes gracefully over time.

## How they actually compare

Here's the comparison table from the project's reference doc:

| Feature | JSON | Protobuf | Avro |
|---|---|---|---|
| Encoding | Text | Binary | Binary |
| Human-readable | Yes | No | No |
| Payload size | Large | Very small | Small |
| Performance | Medium | Very high | High |
| Schema evolution | Moderate | Very good | Excellent |
| Browser support | Yes | No | No |
| Typical use case | Public APIs | Microservices | Data pipelines |

None of these rankings are invented, they're consistent with how each format was designed to work: JSON for readability, Protobuf for speed and small payloads, Avro for long-lived schema evolution.

## Seeing it in code, not just in a table

The demo app exposes three POST endpoints: `/json/user`, `/protobuf/user`, and `/avro/user`. Each one accepts the same logical user (id, name, email, is_active), just encoded differently.

The Avro endpoint uses a schema both client and server agree on ahead of time:

```python
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
```

The Protobuf endpoint checks the content type before it even tries to parse the bytes:

```python
ct = request.headers.get("content-type", "").split(";")[0].strip()
if ct not in ("application/x-protobuf", "application/octet-stream"):
    raise HTTPException(
        status_code=415, detail="Use Content-Type: application/x-protobuf or application/octet-stream"
    )
```

Small detail, but it matters: binary formats don't self-describe the way JSON does, so your API has to be explicit about what it expects. That's a real design cost you take on when you leave text formats behind.

## Where each one actually wins

You don't have to guess. The project docs lay it out plainly:

- **JSON Schema** wins for public-facing REST APIs, browser-based clients, and anything where OpenAPI/Swagger documentation matters.
- **Protobuf** wins for internal service-to-service calls, gRPC, and anywhere bandwidth or serialization speed is the bottleneck.
- **Avro** wins for Kafka topics, long-term data storage, and pipelines where the schema will change for years and old records still need to be readable.

If you're wondering which one is "most used" overall, it's JSON, simply because most public APIs and browser traffic still runs on it. That doesn't make it the best choice everywhere, just the most common one.

## The pattern that actually shows up in production

I've seen this exact layering in more than one real system, and the project's docs describe it well:

```
Frontend / Public APIs        → JSON + JSON Schema (via OpenAPI)
API Gateway / BFF             → translates between layers
Internal Services             → Protobuf + gRPC
Event Streaming / Data Layer  → Avro + Kafka + Schema Registry
```

Your public API stays JSON because your frontend team and third-party integrators need something readable. Your internal services talk Protobuf because every millisecond and every byte counts when you're doing thousands of internal calls per request. Your event stream runs on Avro because a schema registry keeps years of Kafka data usable even as your event shapes evolve.

This isn't a compromise. It's boundary-driven design, and it's a pattern worth having in your back pocket the next time someone insists on a single format for everything.

## What I'd tell a team starting this decision today

- Don't pick a serialization format in the abstract, pick it per boundary, based on who's on the other side of that boundary.
- If humans or browsers touch the payload directly, JSON Schema is still your friend.
- If it's internal service-to-service traffic and performance matters, Protobuf earns its complexity.
- If you're feeding a data pipeline or Kafka topic that will outlive your current team, Avro's schema evolution story pays for itself.
- Try it yourself before you argue about it. Clone the repo, run all three endpoints locally, and look at the actual bytes on the wire.

The full runnable project, with all three endpoints, standalone examples, and tests, is here: [github.com/wallaceespindola/avro-protobuf-jsonschema](https://github.com/wallaceespindola/avro-protobuf-jsonschema).

What's your team's rule for picking a serialization format? Let me know your thoughts in the comments.

---

Need more tech insights?
Check out my GitHub, LinkedIn, and Speaker Deck.
Happy coding!

GitHub: <https://github.com/wallaceespindola/>
LinkedIn: <https://www.linkedin.com/in/wallaceespindola/>

**#softwarearchitecture #java #python #microservices #softwareengineering #apache #grpc**
