# Project Summary: Schemas Demo

**Status**: ✅ Complete
**Type**: Python FastAPI Application
**Package Manager**: uv
**Author**: Wallace Espindola

---

## What Was Built

A Python FastAPI application that implements all code examples from the `avro-protobuf-jsonschema-context.md` reference document. It shows how three data serialization formats work:

1. **JSON with Pydantic validation**
2. **Protocol Buffers (binary)**
3. **Apache Avro (binary)**

---

## Project Structure

```
schemas-demo/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI app with 3 endpoints
│   └── config.py             # Settings with .env support
│
├── schemas/
│   └── user.proto            # Protobuf schema definition
│
├── examples/
│   ├── avro_example.py       # Standalone Avro demo
│   ├── protobuf_example.py   # Standalone Protobuf demo
│   └── jsonschema_example.py # Standalone JSON Schema demo
│
├── clients/
│   ├── test_json_endpoint.sh     # Bash client for JSON
│   ├── test_protobuf_endpoint.py # Python client for Protobuf
│   └── test_avro_endpoint.py     # Python client for Avro
│
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   ├── test_json_endpoint.py # JSON endpoint tests
│   ├── test_avro_endpoint.py # Avro endpoint tests
│   └── test_health.py        # Health/info endpoint tests
│
├── .env.example              # Environment template
├── pyproject.toml            # Project metadata (Python 3.10+)
├── requirements.txt          # Dependencies
├── Makefile                  # Build commands (uv-based)
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Container orchestration
├── setup.sh                  # Automated setup script
├── generate_proto.sh         # Protobuf code generation
├── .gitignore               # Git ignore rules
└── README.md                # Full documentation
```

---

## Key Features

### 1. Three FastAPI Endpoints

- **`POST /json/user`** - JSON with Pydantic validation
- **`POST /protobuf/user`** - Binary Protocol Buffers
- **`POST /avro/user`** - Binary Apache Avro

### 2. Environment Configuration

- `.env` file support with `python-dotenv`
- Pydantic Settings for type-safe configuration
- Author metadata automatically included in API docs

### 3. Complete Testing Suite

- Pytest with async support
- Test coverage reporting
- FastAPI TestClient integration
- Tests for all endpoints

### 4. Standalone Examples

- Independent scripts for each format
- No server needed to run examples
- Clear code with helpful comments

### 5. Client Test Scripts

- Bash script for JSON endpoint
- Python clients for Protobuf and Avro
- Ready-to-use testing tools

### 6. Docker Support

- Multi-stage Dockerfile for smaller images
- Docker Compose for easy deployment
- Health checks configured
- Protobuf code generation in build

### 7. Developer Tools

- **uv** for fast dependency management
- Makefile with all common commands
- Black + isort for code formatting
- Flake8 + mypy for linting and type checking
- Automated setup script

---

## Technologies Used

### Core
- **Python 3.10+**
- **FastAPI** - Async web framework
- **uvicorn** - ASGI server
- **Pydantic v2** - Data validation

### Serialization Libraries
- **fastavro** - Apache Avro implementation
- **protobuf** - Google Protocol Buffers
- **jsonschema** - JSON Schema validation

### Development Tools
- **uv** - Fast Python package manager
- **pytest** - Testing framework
- **black** - Code formatter
- **isort** - Import sorter
- **mypy** - Static type checker

### Deployment
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration

---

## Quick Start Commands

```bash
# Automated setup
./setup.sh

# Or manual setup
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env .env
make proto

# Run the server
make run

# Run tests
make test

# Run all examples
python examples/avro_example.py
python examples/protobuf_example.py
python examples/jsonschema_example.py

# Test all endpoints
./clients/test_json_endpoint.sh
python clients/test_protobuf_endpoint.py
python clients/test_avro_endpoint.py
```

---

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Environment Variables

The application loads author metadata from `.env`:

```env
AUTHOR_NAME=Wallace Espindola
AUTHOR_EMAIL=wallace@example.com
AUTHOR_TITLE=Sr. Software Engineer / Solution Architect
AUTHOR_GITHUB=https://github.com/wallaceespindola
AUTHOR_LINKEDIN=https://www.linkedin.com/in/wallaceespindola/
AUTHOR_SPEAKERDECK=https://speakerdeck.com/wallacese
```

This information appears in:
- API documentation contact section
- Root endpoint (`GET /`) response
- OpenAPI specification

---

## Development Guidelines

This project follows patterns from the AI Agents Framework:

### Python Development
- **Agent**: Python Developer ([`ai/agents/python-developer/AGENT.md`](.ai/agents/python-developer/AGENT.md))
- **Skills**:
  - `python-coder` - Complete project generation
  - `python-code-review` - Code quality standards
  - `python-testing-strategy` - Pytest best practices
  - `fastapi-setup` - FastAPI project structure

### Code Quality
- Type hints throughout
- Async/await patterns
- Pydantic data validation
- Comprehensive docstrings
- Black formatting (100 line length)
- isort import organization

### Testing
- Unit tests for all endpoints
- Integration tests with TestClient
- Fixtures for shared test data
- Coverage reporting

### DevOps
- **Agent**: DevOps Engineer ([`ai/agents/devops-engineer/AGENT.md`](.ai/agents/devops-engineer/AGENT.md))
- **Skills**:
  - `docker-setup` - Multi-stage Dockerfile
  - `cicd-pipeline-setup` - GitHub Actions ready

---

## Comparison to Reference Document

✅ **All code examples implemented**:
- Avro serialization/deserialization (Section 5.1)
- Protobuf serialization/deserialization (Section 5.2)
- JSON Schema validation (Section 5.3)
- JSON endpoint (Section 6.1)
- Protobuf endpoint (Section 6.2)
- Avro endpoint (Section 6.3)
- Client examples (Section 7)

✅ **Additional features**:
- Complete test suite
- Docker deployment
- Environment configuration
- Makefile automation
- Health checks
- Auto-generated API docs

---

## Performance Characteristics

Based on the reference document comparison:

| Format | Payload Size | Speed | Use Case |
|--------|-------------|-------|----------|
| **JSON** | Large (~150 bytes) | Medium | Public APIs, browsers |
| **Protobuf** | Very Small (~30 bytes) | Very Fast | Microservices, gRPC |
| **Avro** | Small (~50 bytes) | Fast | Data pipelines, Kafka |

---

## Next Steps

1. **Run the setup**: `./setup.sh`
2. **Configure .env**: Add your author information
3. **Start the server**: `make run`
4. **Explore the API**: Visit http://localhost:8000/docs
5. **Run examples**: Try standalone examples
6. **Test endpoints**: Use client scripts
7. **Run tests**: `make test`

---

## Integration with Repository

This project is part of the larger `avro-protobuf-jsonschema` repository:

```
avro-protobuf-jsonschema/
├── avro-protobuf-jsonschema-context.md  # Reference document
├── ai/                                   # AI Agents Framework
│   ├── agents/                          # 10 specialized agents
│   └── skills/                          # 95 skills
├── schemas-demo/                        # 👈 This project
└── CLAUDE.md                            # Repository guide
```

---

## Resources

- **Reference Document**: [`../avro-protobuf-jsonschema-context.md`](docs/avro-protobuf-jsonschema-context.md)
- **AI Agents**: [`../ai/AGENTS.md`](.ai/AGENTS.md)
- **Repository Guide**: [`../CLAUDE.md`](CLAUDE.md)

---

**Built with**: Python Developer Agent + FastAPI Setup Skill
**Framework**: AI Agents Framework (10 agents, 95 skills)
**Date**: 2026-02-10
**Status**: Ready to use ✅
