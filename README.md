# Schemas Demo: Avro vs Protobuf vs JSON Schema

A hands-on comparison of three data serialization formats with working FastAPI endpoints. This project shows you how JSON, Protobuf, and Avro work in practice, not just in theory.

All examples come from the reference document: [`avro-protobuf-jsonschema-context.md`](docs/avro-protobuf-jsonschema-context.md)

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Protocol Buffers compiler (`protoc`)

### Quick Installation (Recommended)

```bash
cd schemas-demo
./setup.sh
```

This will:
- Create virtual environment with uv
- Install all dependencies
- Create .env file from template
- Generate Protobuf code (if protoc is installed)

### Manual Installation

1. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and navigate to the project:**
   ```bash
   cd schemas-demo
   ```

3. **Install dependencies using uv:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env .env
   # Edit .env with your author information
   ```

5. **Install Protocol Buffers compiler:**
   ```bash
   # macOS
   brew install protobuf

   # Linux (Debian/Ubuntu)
   apt-get install protobuf-compiler

   # Or download from: https://github.com/protocolbuffers/protobuf/releases
   ```

6. **Generate Protobuf Python code:**
   ```bash
   make proto
   # or
   ./generate_proto.sh
   ```

### Running the Server

```bash
# Using Make
make run

# Or directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### 1. JSON Endpoint (`/json/user`)

Uses Pydantic models with automatic JSON Schema generation via OpenAPI.

**Content-Type**: `application/json`

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

### 2. Protobuf Endpoint (`/protobuf/user`)

Binary Protocol Buffers format - small and fast.

**Content-Type**: `application/x-protobuf`

```bash
# Run the Python client
python clients/test_protobuf_endpoint.py
```

### 3. Avro Endpoint (`/avro/user`)

Binary Avro format - great for schema evolution and data pipelines.

**Content-Type**: `application/avro`

```bash
# Run the Python client
python clients/test_avro_endpoint.py
```

## Project Structure

```
schemas-demo/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application with all endpoints
├── schemas/
│   └── user.proto           # Protobuf schema definition
├── examples/
│   ├── avro_example.py      # Standalone Avro serialization
│   ├── protobuf_example.py  # Standalone Protobuf serialization
│   └── jsonschema_example.py # Standalone JSON Schema validation
├── clients/
│   ├── test_json_endpoint.sh
│   ├── test_protobuf_endpoint.py
│   └── test_avro_endpoint.py
├── tests/
│   ├── test_json_endpoint.py
│   ├── test_avro_endpoint.py
│   └── test_health.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Running Standalone Examples

Try each format with standalone examples:

```bash
# Avro example
python examples/avro_example.py

# Protobuf example (requires: make proto)
python examples/protobuf_example.py

# JSON Schema example
python examples/jsonschema_example.py
```

## Testing

The project has 6 test modules with 30+ tests:

```bash
# Run all tests
make test

# Run with coverage (HTML + terminal report)
make test-cov

# Run tests in watch mode (auto-rerun on changes)
make test-watch

# Run specific endpoint tests
make test-json        # JSON endpoint only
make test-avro        # Avro endpoint only
make test-protobuf    # Protobuf endpoint only
```

**Test Suite:**
- ✅ `test_json_endpoint.py` - JSON/Pydantic validation
- ✅ `test_avro_endpoint.py` - Avro serialization
- ✅ `test_protobuf_endpoint.py` - Protobuf serialization
- ✅ `test_config.py` - Environment configuration
- ✅ `test_health.py` - Health & info endpoints
- ✅ `test_integration.py` - End-to-end API tests

**Coverage**: Target > 85%

See [TESTING.md](docs/TESTING.md) for the full testing guide.

## Client Testing

Test each endpoint with the provided clients:

```bash
# Start the server first
make run

# In another terminal:
./clients/test_json_endpoint.sh
python clients/test_protobuf_endpoint.py
python clients/test_avro_endpoint.py
```

## Docker Deployment

### Build and run with Docker Compose:

```bash
make docker-up
```

Or manually:

```bash
# Build image
docker build -t schemas-demo:latest .

# Run container
docker run -p 8000:8000 schemas-demo:latest
```

## Configuration

The project uses a `.env` file for author metadata and application settings:

```bash
# Copy the example file
cp .env .env

# Edit with your information
nano .env
```

Example `.env` configuration:
```env
AUTHOR_NAME=Wallace Espindola
AUTHOR_EMAIL=wallace@example.com
AUTHOR_TITLE=Sr. Software Engineer / Solution Architect
AUTHOR_BIO=Full-stack developer specializing in Python, Java, and JavaScript
AUTHOR_GITHUB=https://github.com/wallaceespindola
AUTHOR_LINKEDIN=https://www.linkedin.com/in/wallaceespindola/
AUTHOR_SPEAKERDECK=https://speakerdeck.com/wallacese
```

This information is automatically included in:
- API documentation (Swagger/ReDoc)
- Root endpoint (`/`)
- Author attribution

## Makefile Commands

```bash
make help              # Show all available commands
make install           # Install dependencies with uv
make install-dev       # Install with development dependencies
make proto             # Generate Protobuf code
make run               # Run development server
make test              # Run tests
make test-coverage     # Run tests with coverage
make lint              # Lint code
make format            # Format code with black and isort
make clean             # Clean generated files
make docker            # Build Docker image
make docker-up         # Start with Docker Compose
make docker-down       # Stop Docker containers
```

## Format Comparison

| Feature | **JSON** | **Protobuf** | **Avro** |
|---------|----------|--------------|----------|
| **Encoding** | Text | Binary | Binary |
| **Human-readable** | ✅ | ❌ | ❌ |
| **Payload Size** | Large | Very Small | Small |
| **Performance** | Medium | Very High | High |
| **Schema Evolution** | Moderate | Very Good | Excellent |
| **Browser Support** | ✅ | ❌ | ❌ |
| **Use Case** | Public APIs | Microservices | Data Pipelines |

## When to Use Each Format

### JSON Schema
- ✅ Public-facing REST APIs
- ✅ Browser-based applications
- ✅ Human-readable payloads needed
- ✅ OpenAPI/Swagger documentation

### Protocol Buffers
- ✅ Internal microservices communication
- ✅ High-performance requirements
- ✅ Minimal bandwidth usage
- ✅ gRPC services

### Apache Avro
- ✅ Data streaming platforms (Kafka)
- ✅ Long-term data storage
- ✅ Schema evolution critical
- ✅ Big data processing (Spark, Flink)

## Real-World Architecture Pattern

Many production systems use all three formats at different boundaries:

```
Frontend / Public APIs (JSON + JSON Schema via OpenAPI)
                ↓
        API Gateway / BFF
                ↓
   Internal Services (Protobuf + gRPC)
                ↓
Event Streaming / Data Platform (Avro + Kafka + Schema Registry)
```

## Reference Documentation

- **Main Reference**: [`avro-protobuf-jsonschema-context.md`](docs/avro-protobuf-jsonschema-context.md) - Deep dive into format comparisons
- **AI Agents Framework**: [`ai/`](../ai/) - 10 agents and 95 skills for development automation

## Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint
```

### Type Checking

```bash
mypy app
```

## Troubleshooting

### Protobuf module not found

If you see "Protobuf module not generated":
1. Install `protoc`: `brew install protobuf` (macOS) or `apt-get install protobuf-compiler` (Linux)
2. Run: `make proto` or `./generate_proto.sh`

### Port already in use

If port 8000 is already in use, change the port:
```bash
uvicorn app.main:app --reload --port 8001
```

## Documentation

- **[README.md](README.md)** - Main docs (you're reading this)
- **[TESTING.md](docs/TESTING.md)** - Testing guide
- **[COMMANDS.md](docs/COMMANDS.md)** - Command reference (50+ commands)
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Tech overview
- **[PRE-COMMIT.md](docs/PRE-COMMIT.md)** - Pre-commit hooks
- **[PRE-COMMIT-SETUP.md](docs/PRE-COMMIT-SETUP.md)** - Setup guide
- **[PRE-COMMIT-WORKFLOW.md](docs/PRE-COMMIT-WORKFLOW.md)** - Workflow
- **[PRE-COMMIT-CHECKLIST.md](docs/PRE-COMMIT-CHECKLIST.md)** - Checklist
- **[PRE-COMMIT-QUICKREF.md](docs/PRE-COMMIT-QUICKREF.md)** - Quick reference
- **[PRE-COMMIT-INDEX.md](docs/PRE-COMMIT-INDEX.md)** - Hooks index
- **[PRE-COMMIT-SUMMARY.md](docs/PRE-COMMIT-SUMMARY.md)** - Summary
- **[CONFIGURATION-UPDATES.md](docs/CONFIGURATION-UPDATES.md)** - Config updates

## Contributing

Before committing:
```bash
make format    # Format code
make ci        # Run all checks (lint, type-check, tests)
```

Python development guidelines:
- **Development**: See [`ai/agents/python-developer/AGENT.md`](.ai/agents/python-developer/AGENT.md)
- **Testing**: See [`ai/skills/python-testing-strategy/SKILL.md`](.ai/skills/python-testing-strategy/SKILL.md)
- **Code Review**: See [`ai/skills/python-code-review/SKILL.md`](.ai/skills/python-code-review/SKILL.md)

## License

This project is part of the avro-protobuf-jsonschema comparison repository.

---

**Author**: Wallace Espindola
**Reference**: [avro-protobuf-jsonschema-context.md](docs/avro-protobuf-jsonschema-context.md)

*Also check out the [AI Agents Framework](../ai/) with 10 agents and 95 skills for development automation.*
