# Testing Guide

Everything you need to know about testing this project.

## Quick Start

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
make test-json        # JSON endpoint tests
make test-avro        # Avro endpoint tests
make test-protobuf    # Protobuf endpoint tests
```

## Test Suite Overview

The project has **6 test modules** covering all the endpoints and features:

### 1. JSON Endpoint Tests (`test_json_endpoint.py`)

Tests for the JSON endpoint with Pydantic validation:

- ✅ Valid user data with all fields
- ✅ Minimal user data (required fields only)
- ✅ Invalid ID validation (< 1)
- ✅ Missing required fields
- ✅ Empty string validation

**Run**: `make test-json` or `uv run pytest tests/test_json_endpoint.py -v`

### 2. Avro Endpoint Tests (`test_avro_endpoint.py`)

Tests for the Avro binary endpoint:

- ✅ Valid Avro serialization/deserialization
- ✅ Minimal fields with defaults
- ✅ Invalid ID validation
- ✅ Wrong content type rejection
- ✅ Invalid payload handling

**Run**: `make test-avro` or `uv run pytest tests/test_avro_endpoint.py -v`

### 3. Protobuf Endpoint Tests (`test_protobuf_endpoint.py`)

Tests for the Protobuf binary endpoint:

- ✅ Valid Protobuf serialization/deserialization
- ✅ Minimal fields
- ✅ Invalid ID validation
- ✅ Wrong content type rejection
- ✅ Invalid payload handling
- ✅ Alternative content type (octet-stream)

**Run**: `make test-protobuf` or `uv run pytest tests/test_protobuf_endpoint.py -v`

**Note**: Requires `make proto` to generate Protobuf code first.

### 4. Configuration Tests (`test_config.py`)

Tests for environment configuration:

- ✅ Default settings values
- ✅ Environment variable overrides
- ✅ Case-insensitive env vars
- ✅ Settings caching (lru_cache)
- ✅ Link format validation

**Run**: `uv run pytest tests/test_config.py -v`

### 5. Health & Info Tests (`test_health.py`)

Tests for utility endpoints:

- ✅ Root endpoint information
- ✅ Health check endpoint
- ✅ Protobuf availability status

**Run**: `uv run pytest tests/test_health.py -v`

### 6. Integration Tests (`test_integration.py`)

End-to-end tests for the complete API:

- ✅ API documentation availability (OpenAPI, Swagger, ReDoc)
- ✅ Contact information in OpenAPI spec
- ✅ All endpoints listed in root
- ✅ Author information in responses
- ✅ Complete round-trip for each format
- ✅ Same data across all formats
- ✅ CORS configuration

**Run**: `uv run pytest tests/test_integration.py -v`

## Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run fast (stop on first failure)
make test-fast

# Re-run only failed tests
make test-failed
```

### Coverage Reports

```bash
# Run tests with coverage
make test-cov

# View HTML coverage report
open htmlcov/index.html

# Coverage is saved to:
# - htmlcov/          (HTML report)
# - coverage.xml      (XML for CI)
# - .coverage         (SQLite database)
```

### Watch Mode

```bash
# Auto-run tests on file changes (requires pytest-watch)
make test-watch
```

### Specific Test Files

```bash
# Run specific test module
uv run pytest tests/test_json_endpoint.py -v

# Run specific test function
uv run pytest tests/test_json_endpoint.py::test_json_endpoint_valid_user -v

# Run tests matching pattern
uv run pytest -k "json" -v
```

## Test Markers

Tests can be marked for selective execution:

```bash
# Run only slow tests
uv run pytest -m "slow" -v

# Skip slow tests
uv run pytest -m "not slow" -v

# Run only integration tests
uv run pytest -m "integration" -v

# Run tests requiring Protobuf
uv run pytest -m "requires_protobuf" -v
```

## Testing Individual Formats

### Testing JSON Format

```bash
# Run JSON tests
make test-json

# Test manually with curl
make dev  # In one terminal
./clients/test_json_endpoint.sh  # In another terminal
```

### Testing Avro Format

```bash
# Run Avro tests
make test-avro

# Test manually
make dev  # In one terminal
uv run python clients/test_avro_endpoint.py  # In another
```

### Testing Protobuf Format

```bash
# Generate Protobuf code first
make proto

# Run Protobuf tests
make test-protobuf

# Test manually
make dev  # In one terminal
uv run python clients/test_protobuf_endpoint.py  # In another
```

## Test Fixtures

The test suite uses pytest fixtures defined in `tests/conftest.py`:

- `client` - FastAPI TestClient instance
- `avro_schema` - Parsed Avro schema

## Coverage Goals

Target coverage: **> 85%**

Current coverage areas:
- ✅ All API endpoints
- ✅ Request validation
- ✅ Error handling
- ✅ Configuration loading
- ✅ Serialization/deserialization
- ✅ Content type validation

Excluded from coverage:
- Generated Protobuf code (`*_pb2.py`)
- Test files themselves
- Type checking blocks

## CI/CD Integration

Tests run automatically in GitHub Actions on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

CI workflow (`.github/workflows/ci.yml`):
1. Tests on Python 3.10, 3.11, 3.12
2. Linting (flake8)
3. Type checking (mypy)
4. Format checking (black, isort)
5. Tests with coverage
6. Coverage upload to Codecov
7. Docker image build and test

## Writing New Tests

### Test Structure

```python
def test_feature_name(client: TestClient) -> None:
    """Test description."""
    # Arrange
    payload = {...}

    # Act
    response = client.post("/endpoint", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["field"] == expected_value
```

### Best Practices

1. **Use descriptive names**: `test_json_endpoint_invalid_id` not `test_1`
2. **One assertion per test** (when possible)
3. **Test both success and failure** cases
4. **Use fixtures** for common setup
5. **Add docstrings** explaining what is being tested
6. **Mark slow tests** with `@pytest.mark.slow`
7. **Test edge cases**: empty strings, null values, boundary conditions

### Example Test

```python
def test_json_endpoint_boundary_id(client: TestClient) -> None:
    """Test JSON endpoint with boundary ID value (exactly 1)."""
    payload = {
        "id": 1,  # Minimum valid value
        "name": "Test",
        "is_active": True
    }

    response = client.post("/json/user", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == 1
```

## Troubleshooting

### Protobuf Tests Failing

```bash
# Generate Protobuf code
make proto

# Verify generation
ls -la schemas/user_pb2.py
```

### Import Errors

```bash
# Reinstall in editable mode
uv pip install -e ".[dev]"
```

### Coverage Not Generated

```bash
# Install coverage plugin
uv pip install pytest-cov

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

### Tests Hang

```bash
# Run with timeout
uv run pytest --timeout=10
```

## Testing Checklist

Before committing:

- [ ] All tests pass: `make test`
- [ ] Coverage > 85%: `make test-cov`
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `make type-check`
- [ ] Format checked: `make format-check`
- [ ] All checks pass: `make ci`

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Coverage.py**: https://coverage.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/

---

**Questions?** See the main [README.md](README.md) or open an issue.
