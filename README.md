![Python](https://www.python.org/static/community_logos/python-logo-generic.svg)

# ⚡ Avro vs Protobuf vs JSON Schema

**One FastAPI app. Three serialization formats. Real, runnable code.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Protobuf](https://img.shields.io/badge/Protobuf-binary-4285F4?logo=google&logoColor=white)](https://protobuf.dev/)
[![Avro](https://img.shields.io/badge/Apache%20Avro-schema%20evolution-231F20?logo=apache&logoColor=white)](https://avro.apache.org/)
[![Tests](https://img.shields.io/badge/tests-34%20passing-brightgreen)](tests/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Most format comparisons stop at a table. This project goes further: the same `User` payload served over JSON, Protocol Buffers and Apache Avro from a single API, with standalone examples, test clients and a full test suite. Clone it, run it, inspect the bytes yourself.

---

## 🚀 Quick Start

```bash
git clone https://github.com/wallaceespindola/avro-protobuf-jsonschema.git
cd avro-protobuf-jsonschema
./setup.sh     # venv + dependencies + .env + protobuf codegen
make run       # server on http://localhost:8000
```

<details>
<summary><b>Manual setup</b></summary>

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Dependencies
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Protobuf compiler
brew install protobuf          # macOS
apt-get install protobuf-compiler  # Debian/Ubuntu

# Generate Protobuf code
make proto
```

</details>

Once running:

| URL | What |
|-----|------|
| <http://localhost:8000/docs> | Swagger UI |
| <http://localhost:8000/redoc> | ReDoc |
| <http://localhost:8000/health> | Health check |

## 🔌 The Three Endpoints

### `POST /json/user` — JSON

Pydantic models, automatic JSON Schema via OpenAPI. `Content-Type: application/json`

```bash
curl -X POST http://localhost:8000/json/user \
  -H "Content-Type: application/json" \
  -d '{"id":1,"name":"Wallace","email":"wallace@example.com","is_active":true}'
```

### `POST /protobuf/user` — Protocol Buffers

Compact binary, generated from [`schemas/user.proto`](schemas/user.proto). `Content-Type: application/x-protobuf`

```bash
python clients/test_protobuf_endpoint.py
```

### `POST /avro/user` — Apache Avro

Binary with first-class schema evolution. `Content-Type: application/avro`

```bash
python clients/test_avro_endpoint.py
```

## ⚖️ Format Comparison

| | **JSON** | **Protobuf** | **Avro** |
|---|:---:|:---:|:---:|
| Encoding | Text | Binary | Binary |
| Human-readable | ✅ | ❌ | ❌ |
| Payload size | Large | Very small | Small |
| Performance | Medium | Very high | High |
| Schema evolution | Moderate | Very good | Excellent |
| Browser support | ✅ | ❌ | ❌ |
| Sweet spot | Public APIs | Microservices | Data pipelines |

**Pick by boundary, not by taste:**

- 🌐 **JSON Schema** — public REST APIs, browsers, OpenAPI docs
- 🔗 **Protobuf** — internal service-to-service traffic, gRPC, tight bandwidth
- 🌊 **Avro** — Kafka streaming, long-term storage, Spark/Flink pipelines

Real systems often use all three at once:

```text
Frontend / Public APIs ──── JSON + JSON Schema (OpenAPI)
          │
    API Gateway / BFF
          │
Internal Services ────────── Protobuf + gRPC
          │
Event Streaming ──────────── Avro + Kafka + Schema Registry
```

Deep dive: [`docs/avro-protobuf-jsonschema-context.md`](docs/avro-protobuf-jsonschema-context.md)

## 🧪 Try Each Format Standalone

```bash
python examples/jsonschema_example.py   # validate against a JSON Schema
python examples/protobuf_example.py     # serialize/deserialize Protobuf (needs: make proto)
python examples/avro_example.py         # serialize/deserialize Avro
```

## ✅ Testing

34 tests across 6 modules — endpoints, config, health and end-to-end flows.

```bash
make test         # full suite
make test-cov     # with coverage report
make test-json    # one endpoint at a time
make test-avro
make test-protobuf
```

Full guide: [`docs/TESTING.md`](docs/TESTING.md)

## 🐳 Docker

```bash
make docker-up    # docker compose up

# or manually
docker build -t schemas-demo:latest .
docker run -p 8000:8000 schemas-demo:latest
```

## 🛠️ Development

```bash
make help      # all commands
make format    # black + isort
make lint      # ruff
make ci        # lint + type-check + tests
```

Configuration lives in `.env` (author metadata shown in the API docs and root endpoint) — copy from the template and edit.

<details>
<summary><b>Troubleshooting</b></summary>

**"Protobuf module not generated"** — install `protoc` (`brew install protobuf` / `apt-get install protobuf-compiler`), then `make proto`.

**Port 8000 busy** — `uvicorn app.main:app --reload --port 8001`

</details>

## 📁 Project Layout

```text
├── app/           # FastAPI application (all three endpoints)
├── schemas/       # user.proto — Protobuf schema
├── examples/      # standalone serialization examples
├── clients/       # endpoint test clients (curl + Python)
├── tests/         # pytest suite
├── docs/          # reference documentation
├── Dockerfile / docker-compose.yml
└── Makefile
```

## 📄 License

- Released under the [Apache 2.0 License](LICENSE)
- Copyright © 2026 [Wallace Espindola](https://github.com/wallaceespindola/)

## 👤 Author

**Wallace Espindola** — Sr. Software Engineer / Solution Architect / Java & Python Dev

[![LinkedIn](https://img.shields.io/badge/LinkedIn-wallaceespindola-0A66C2?logo=linkedin)](https://www.linkedin.com/in/wallaceespindola/)
[![GitHub](https://img.shields.io/badge/GitHub-wallaceespindola-181717?logo=github)](https://github.com/wallaceespindola/)
[![Email](https://img.shields.io/badge/Email-wallace.espindola%40gmail.com-EA4335?logo=gmail&logoColor=white)](mailto:wallace.espindola@gmail.com)

- **LinkedIn:** [linkedin.com/in/wallaceespindola](https://www.linkedin.com/in/wallaceespindola/)
- **GitHub:** [github.com/wallaceespindola](https://github.com/wallaceespindola)
- **E-mail:** [wallace.espindola@gmail.com](mailto:wallace.espindola@gmail.com)
- **Twitter/X:** [@wsespindola](https://twitter.com/wsespindola)
- **Gravatar:** [gravatar.com/wallacese](https://gravatar.com/wallacese)
- **Dev Community:** [dev.to/wallaceespindola](https://dev.to/wallaceespindola)
- **DZone Articles:** [DZone Profile](https://dzone.com/users/1254611/wallacese.html)
- **Pulse LinkedIn:** [LinkedIn Articles](https://www.linkedin.com/in/wallaceespindola/recent-activity/articles/)
- **Website:** [W-Tech IT Solutions](https://www.wtechitsolutions.com/)
- **Substack:** [wallaceespindola.substack.com](https://wallaceespindola.substack.com/)
- **Medium:** [medium.com/@wallaceespindola](https://medium.com/@wallaceespindola)
- **Slides:** [speakerdeck.com/wallacese](https://speakerdeck.com/wallacese)

---

⭐ If this repo helped you pick a serialization format, a star helps others find it.
