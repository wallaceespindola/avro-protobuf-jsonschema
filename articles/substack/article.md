![Banner](banner.png)

# Three Formats Walk Into an API: A Field Guide to Avro, Protobuf and JSON Schema

Hey folks,

A few weeks back I got pulled into a conversation that I bet you've had a version of too: "why don't we just use JSON for everything?" It came up during a design review for a service that sits between a public API, a handful of internal microservices, and a Kafka pipeline. Reasonable question. Also, kind of the wrong question.

The real question isn't "which format is best." It's "what is this data contract actually for, and who has to read it." A payload your frontend renders in a browser has different needs than a message your fraud-detection service pulls off a Kafka topic five years from now. Once I started answering it that way, the whole "one format to rule them all" debate stopped making sense.

So instead of writing another opinion post, I built the thing. I put together a small FastAPI app with three endpoints — one JSON, one Protobuf, one Avro — all serializing the same `User` object, so you can see the differences instead of just reading about them. That's what this issue is about.

## The three contenders, in plain language

**JSON Schema** is the one you already know, whether you call it that or not. It's a way to describe and validate the shape of a JSON document. When your FastAPI app uses Pydantic models, it's generating JSON Schema behind the scenes for your OpenAPI docs. Text-based, human-readable, works in every browser without a library.

**Protocol Buffers (Protobuf)** trades readability for size and speed. You write a `.proto` file describing your message, run it through a compiler, and get generated code in whatever language you need. The payload on the wire is binary and compact. This is the backbone of a lot of gRPC-based microservice communication.

**Apache Avro** is also binary, but its whole reason for existing is schema evolution. It's built for situations where the schema and the data need to travel together or live in a registry, which is exactly what you want when a Kafka topic might be read by a consumer that's still running last quarter's code.

None of these is "wrong." They're built for different jobs.

## The comparison, side by side

Here's the table I keep coming back to when someone asks me to justify a format choice in a design doc:

| Feature | JSON | Protobuf | Avro |
|---|---|---|---|
| Encoding | Text | Binary | Binary |
| Human-readable | Yes | No | No |
| Payload size | Large | Very small | Small |
| Schema evolution | Moderate | Very good | Excellent |
| Browser support | Yes | No | No |
| Typical home | Public APIs | Microservices / gRPC | Data pipelines / Kafka |

Nothing revolutionary here, but writing it down like this made the design review a lot shorter. Instead of arguing in circles, we just asked: is this boundary public-facing, internal-service-to-service, or streaming data that needs to survive schema changes over years? The format basically picked itself after that.

## What the code actually looks like

I won't paste the whole app here — email clients mangle long code blocks, and you can just clone the repo — but here's a taste of each format so you can see how different the developer experience is.

Defining a user in Avro is just a schema dictionary:

```python
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
```

Protobuf wants a `.proto` file, compiled ahead of time:

```proto
message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  bool is_active = 4;
}
```

And JSON Schema, if you're using Pydantic, you barely have to think about it. You just write a model and FastAPI generates the schema for your OpenAPI docs automatically:

```python
class UserJSON(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    email: str | None = None
    is_active: bool = True
```

That last point is worth sitting with for a second. With JSON and Pydantic, the "schema work" is almost invisible — it falls out of writing normal code. With Protobuf, you're running a compiler step (`protoc`) before you can use your own message type. With Avro, you're usually pairing the schema with a registry if you're doing anything serious in Kafka. That operational overhead is the real cost of the extra guarantees you get, and it's easy to forget until you're the one debugging why a consumer can't read a message a producer just sent.

## Try it yourself

I put all of this into a working repo instead of leaving it as a slide deck nobody runs:

**https://github.com/wallaceespindola/avro-protobuf-jsonschema**

It's a real FastAPI app, not a snippet collection. Clone it, and you get:

- `/json/user`, `/protobuf/user` and `/avro/user` — three live endpoints doing the same job in three formats
- Standalone examples in `examples/` if you just want to see serialization and deserialization without spinning up a server
- Client scripts in `clients/` so you can hit each endpoint and watch the responses come back
- A full pytest suite covering all three formats plus health checks

Getting it running is a few commands:

```bash
git clone https://github.com/wallaceespindola/avro-protobuf-jsonschema
cd avro-protobuf-jsonschema
./setup.sh
make run
```

Once it's up, open `http://localhost:8000/docs` for the Swagger UI, or just run the standalone examples directly:

```bash
python examples/avro_example.py
python examples/protobuf_example.py
python examples/jsonschema_example.py
```

The Avro and Protobuf ones print the serialized byte counts and the decoded objects, so you can literally watch a Python dict turn into binary and back; the JSON Schema one walks through validation passing and failing. It's a small thing, but seeing the byte counts side by side does more to make the size argument real than any comparison table.

If you want the deeper write-up with every endpoint's full source and the client-side test code, the repo's reference doc walks through it end to end: [`docs/avro-protobuf-jsonschema-context.md`](https://github.com/wallaceespindola/avro-protobuf-jsonschema/blob/main/docs/avro-protobuf-jsonschema-context.md).

## The pattern I actually use

The thing that clicked for me while building this: mature systems don't pick one format. They pick a format per boundary. The pattern that comes up over and over looks like this:

```
Frontend / public APIs → JSON + JSON Schema (via OpenAPI)
        ↓
API Gateway / BFF
        ↓
Internal services → Protobuf + gRPC
        ↓
Event streaming / data platform → Avro + Kafka + schema registry
```

That's not over-engineering. It's matching the format to what that layer actually needs. Your public API needs to be readable by a browser and debuggable with curl. Your internal services need speed and small payloads because they're chatting with each other thousands of times a second. Your event stream needs to survive a producer and consumer being on different versions of the schema for months.

A few things worth knowing before you commit to any of these in production:

- Proto3 has quirks around field presence — an unset `string` and an empty string look the same unless you use `optional` or wrapper types. Bit me once, won't happen again.
- Avro over plain HTTP is usually "schemaless," meaning the schema isn't in the payload — both sides just need to agree on it ahead of time. For Kafka, you'll almost always want an actual schema registry rather than trusting that agreement to hold forever.
- JSON Schema is the easiest to get right by accident and the easiest to get wrong on purpose — nothing stops a client from sending garbage unless your validation is actually strict.

## Wrapping up

If there's one takeaway I'd want you to walk away with, it's this: stop asking "which serialization format is best" and start asking "what does this specific boundary in my system actually need." Readability for humans? Raw speed for internal calls? Years of schema evolution for a data lake? The answer changes the format, and that's fine — using three formats in one architecture isn't a compromise, it's the design working as intended.

Go pull the repo, run the endpoints, and watch the byte counts for yourself. It's a better argument than anything I could write here.

What's your setup — do you run one format everywhere, or mix them by boundary like this? Hit reply or drop a comment, I read every one.

Need more tech insights?
Check out my GitHub, LinkedIn, and Speaker Deck.
Happy coding!

— Wallace

GitHub: https://github.com/wallaceespindola/
LinkedIn: https://www.linkedin.com/in/wallaceespindola/
Email: wallace.espindola@gmail.com
